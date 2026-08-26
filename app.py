"""Supply Chain Risk Engine V2.1 — Enterprise B2B Terminal."""
from __future__ import annotations
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

import plotly.express as px
import polars as pl
import streamlit as st

import theme
from ai.narrative_generator import generate as generate_narratives
from ai.news_digest import generate_news_digest
from engine.risk_scoring import score_suppliers
from feeds.rss_client import RSS_SOURCES, fetch_news
from feeds.weather_client import fetch_weather
from geo.map_builder import build_map, render_in_streamlit
from ingestion.validation_gate import IngestionError, ingest_supplier_csv
from reporting.html_report import render_html_report
from reporting.pdf_report import render_pdf_report
from resilience.http_client import classify_error
from schemas.scenario_schema import RiskWeighting, ScenarioConfig
from state.session_contract import (
    complete, init_session_state, is_done, make_weather_key,
    news_is_stale, register_upload, scenario_key,
)
from telemetry.logger import configure_logging, logger
from telemetry.streamlit_handler import StreamlitLogHandler

try: st.set_page_config(page_title="Risk Engine // V2.1 Enterprise", layout="wide", page_icon="◈")
except Exception: pass

init_session_state(st.session_state)
configure_logging()

log_handler = StreamlitLogHandler(buffer=st.session_state["log_buffer"])
log_handler.attach()

st.markdown(theme.inject_theme_css(), unsafe_allow_html=True)
st.markdown(theme.brand_bar(), unsafe_allow_html=True)
st.markdown(theme.ops_strip(), unsafe_allow_html=True)

if st.session_state["last_error"]:
    st.error(st.session_state["last_error"])
    st.session_state["last_error"] = None

with st.sidebar:
    st.markdown('<div class="obs-micro">System Diagnostics</div>', unsafe_allow_html=True)
    log_handler.render()

# ── Data Ingestion Gateway ────────────────────────────────
st.markdown('<div class="obs-micro">Data Ingestion Gateway</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload supplier CSV to initialize the risk pipeline", type=["csv"], label_visibility="collapsed")

if uploaded_file is None:
    st.markdown('<div class="obs-empty">◈ · AWAITING DATA INGESTION · UPLOAD SUPPLIER CSV TO INITIALIZE RISK PIPELINE</div>', unsafe_allow_html=True)
else:
    upload_bytes = uploaded_file.getvalue()
    is_new_upload = register_upload(st.session_state, upload_bytes)
    if is_new_upload:
        st.session_state.pop("map_obj", None)
        logger.bind(request_id=st.session_state["raw_upload_hash"][:8]).info("New upload registered; downstream stages invalidated.")

    if not is_done(st.session_state, "validation_done"):
        try:
            with st.spinner("Validating schema boundary..."):
                validated_df = ingest_supplier_csv(upload_bytes)
                st.session_state["validated_df"] = validated_df
                complete(st.session_state, "validation_done")
                logger.info(f"Validation complete: {validated_df.height} rows")
        except IngestionError as exc:
            category = classify_error(exc)
            st.session_state["validation_errors"] = exc.failure_cases
            st.session_state["last_error"] = f"[{category}] Schema validation rejected the payload."
            logger.error(f"Validation failed [{category}]: {exc}")
            st.stop()
        except Exception as exc:
            category = classify_error(exc)
            st.session_state["last_error"] = f"[{category}] Ingestion pipeline fault."
            logger.exception(f"Ingestion failed [{category}]")
            st.stop()

    if is_done(st.session_state, "validation_done"):
        tab_dash, tab_map, tab_intel, tab_weather, tab_reports = st.tabs(
            ["Portfolio Risk", "Geospatial Topology", "Macro Intelligence", "Environmental", "Executive Briefing"]
        )

        with tab_dash:
            st.markdown('<div class="obs-micro">Strategic Scenario Modeling</div>', unsafe_allow_html=True)
            existing_config = st.session_state.get("scenario_config")
            default_name = existing_config.scenario_name if existing_config else "Baseline Exposure"
            default_regions = existing_config.regions if existing_config else ["EMEA", "APAC", "NA", "LATAM"]
            default_min = existing_config.min_risk_threshold if existing_config else 0.0
            default_max = existing_config.max_risk_threshold if existing_config else 1.0
            weighting_options = list(RiskWeighting)
            default_weighting_index = weighting_options.index(existing_config.weighting) if existing_config else 0

            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 2, 2])
                with c1:
                    scenario_name = st.text_input("Scenario Designation", value=default_name, key="scenario_name")
                    regions = st.multiselect("Geographic Scope", ["EMEA", "APAC", "NA", "LATAM"], default=default_regions, key="regions")
                with c2:
                    min_risk = st.slider("Minimum Risk Threshold", 0.0, 1.0, default_min, key="min_risk")
                    max_risk = st.slider("Maximum Risk Threshold", 0.0, 1.0, default_max, key="max_risk")
                with c3:
                    weighting = st.selectbox("Risk Weighting Model", weighting_options, index=default_weighting_index, format_func=lambda item: item.value.replace("_", " ").title(), key="weighting")
                    if st.button("◈ Execute Scenario", key="apply_scenario", type="primary"):
                        try:
                            config = ScenarioConfig(scenario_name=scenario_name, regions=regions, min_risk_threshold=min_risk, max_risk_threshold=max_risk, weighting=weighting)
                            if existing_config != config:
                                st.session_state["scenario_config"] = config
                                st.session_state["scoring_done"] = False
                                st.session_state["ai_generation_done"] = False
                                st.session_state["ai_narratives"] = {}
                                st.session_state["report_pdf_bytes"] = None
                                st.session_state["report_html_str"] = None
                                st.session_state.pop("map_obj", None)
                                logger.info(f"Scenario applied: {config.scenario_name}")
                        except Exception as exc:
                            category = classify_error(exc)
                            st.session_state["last_error"] = f"[{category}] Invalid scenario parameters."
                            logger.error(f"Invalid scenario [{category}]: {exc}")

            if st.session_state.get("scenario_config") is not None and not is_done(st.session_state, "scoring_done"):
                try:
                    with st.spinner("Executing vectorized risk scoring..."):
                        scored_df = score_suppliers(st.session_state["validated_df"], st.session_state["scenario_config"])
                        st.session_state["scored_df"] = scored_df
                        complete(st.session_state, "scoring_done")
                        logger.info(f"Scoring complete: {scored_df.height} suppliers")
                except Exception as exc:
                    category = classify_error(exc)
                    st.session_state["last_error"] = f"[{category}] Scoring engine fault."
                    logger.exception(f"Scoring failed [{category}]")

            if is_done(st.session_state, "scoring_done"):
                scored_df = st.session_state["scored_df"]
                st.markdown('<div class="obs-micro" style="margin-top: 24px;">Portfolio Risk Metrics</div>', unsafe_allow_html=True)
                k1, k2, k3, k4 = st.columns(4)
                total_suppliers = scored_df.height
                avg_risk = float(scored_df["composite_risk"].mean()) if "composite_risk" in scored_df.columns else 0.0
                high_risk = scored_df.filter(pl.col("composite_risk") >= 0.7).height if "composite_risk" in scored_df.columns else 0
                critical_count = scored_df.filter(pl.col("composite_risk") >= 0.85).height if "composite_risk" in scored_df.columns else 0

                with k1: st.markdown(theme.kpi_card("Total Entities", f"{total_suppliers:,}", accent="cyan"), unsafe_allow_html=True)
                with k2: st.markdown(theme.kpi_card("Portfolio Risk Index", f"{avg_risk:.3f}", delta=f"{avg_risk*100:.1f}%", delta_dir="neutral", accent="indigo"), unsafe_allow_html=True)
                with k3: st.markdown(theme.kpi_card("High Exposure (≥0.70)", f"{high_risk:,}", accent="risk_high"), unsafe_allow_html=True)
                with k4: st.markdown(theme.kpi_card("Critical Exposure (≥0.85)", f"{critical_count:,}", accent="risk_critical"), unsafe_allow_html=True)

                if "region" in scored_df.columns and "composite_risk" in scored_df.columns:
                    region_agg = scored_df.group_by("region").agg([pl.col("composite_risk").mean().alias("avg_risk"), pl.col("supplier_id").count().alias("count")]).sort("avg_risk", descending=True)
                    fig = px.bar(
                        region_agg.to_pandas() if hasattr(region_agg, "to_pandas") else region_agg,
                        x="region", y="avg_risk", color="avg_risk",
                        color_discrete_sequence=[theme.DESIGN_TOKENS["accent"], theme.DESIGN_TOKENS["accent_2"]],
                        custom_data=["count"],
                    )
                    fig.update_layout(
                        title={"text": "Regional Risk Concentration", "x": 0.02, "y": 0.95, "font": {"size": 14, "color": theme.DESIGN_TOKENS["text_1"]}},
                        xaxis_title="Geographic Region", yaxis_title="Composite Risk Index", showlegend=False,
                        **theme.get_plotly_layout(),
                    )
                    fig.update_traces(
                        hovertemplate="<b>%{x}</b><br>Risk Index: %{y:.3f}<br>Entities: %{customdata[0]}<extra></extra>",
                        marker_line_width=0,
                    )
                    st.plotly_chart(fig, use_container_width=True)

                st.markdown('<div class="obs-micro" style="margin-top: 24px;">Entity Risk Matrix</div>', unsafe_allow_html=True)
                display_df = scored_df.sort("composite_risk", descending=True).select(["supplier_id", "supplier_name", "region", "tier", "composite_risk", "annual_spend_usd"])
                st.dataframe(
                    display_df, use_container_width=True, hide_index=True, height=400,
                    column_config={
                        "supplier_id": st.column_config.TextColumn("Entity ID", width="small"),
                        "supplier_name": st.column_config.TextColumn("Entity Name", width="medium"),
                        "region": st.column_config.TextColumn("Region", width="small"),
                        "tier": st.column_config.NumberColumn("Tier", width="small"),
                        "composite_risk": st.column_config.ProgressColumn("Risk Index", min_value=0.0, max_value=1.0, format="%.3f", width="small"),
                        "annual_spend_usd": st.column_config.NumberColumn("Annual Spend", format="$%s", width="small"),
                    },
                )

                if st.session_state["scenario_config"].include_ai_narrative:
                    st.markdown('<div class="obs-micro" style="margin-top: 24px;">AI-Driven Risk Narratives</div>', unsafe_allow_html=True)
                    if not is_done(st.session_state, "ai_generation_done"):
                        try:
                            with st.spinner("Synthesizing narratives via Gemini..."):
                                rows = scored_df.head(10).to_dicts()
                                narratives = generate_narratives(rows)
                                st.session_state["ai_narratives"] = narratives
                                st.session_state["ai_call_count"] += 1
                                complete(st.session_state, "ai_generation_done")
                                logger.info(f"AI narratives generated: {len(narratives)}")
                        except Exception as exc:
                            category = classify_error(exc)
                            st.session_state["last_error"] = f"[{category}] AI synthesis fault."
                            logger.exception(f"AI generation failed [{category}]")

                    if st.session_state.get("ai_narratives"):
                        for supplier_id, narrative in st.session_state["ai_narratives"].items():
                            with st.expander(f"{narrative.supplier_name} // {supplier_id}"):
                                st.markdown(theme.status_pill(narrative.overall_risk), unsafe_allow_html=True)
                                st.markdown(f"**Key Risk Vectors:** {', '.join(narrative.key_risks)}")
                                st.markdown(f"**Strategic Recommendation:** {narrative.recommendation}")
                                st.caption(f"Model Confidence: {narrative.confidence:.2f}")

        with tab_map:
            st.markdown('<div class="obs-micro">Geospatial Risk Topology</div>', unsafe_allow_html=True)
            if not is_done(st.session_state, "scoring_done"):
                st.markdown('<div class="obs-empty">◈ · EXECUTE A SCENARIO IN PORTFOLIO RISK TO RENDER GEOSPATIAL TOPOLOGY</div>', unsafe_allow_html=True)
            else:
                scored_df = st.session_state["scored_df"]
                if not is_done(st.session_state, "map_render_done") or "map_obj" not in st.session_state:
                    try:
                        with st.spinner("Building FastMarkerCluster payload..."):
                            map_obj = build_map(scored_df, st.session_state["scenario_config"])
                            st.session_state["map_obj"] = map_obj
                            complete(st.session_state, "map_render_done")
                    except Exception as exc:
                        category = classify_error(exc)
                        st.session_state["last_error"] = f"[{category}] Map render fault."
                        logger.exception(f"Map rendering failed [{category}]")
                if "map_obj" in st.session_state:
                    render_in_streamlit(st.session_state["map_obj"])

        with tab_intel:
            st.markdown('<div class="obs-micro">Macro-Environmental Intelligence</div>', unsafe_allow_html=True)
            keywords = st.text_input("Keyword Filters (comma-separated)", value="port, strike, disruption, shortage, tariff", key="news_keywords")
            selected_sources = st.multiselect("Intelligence Sources", options=list(RSS_SOURCES.keys()), default=list(RSS_SOURCES.keys()), key="news_sources")
            force_refresh = st.checkbox("Force cache bypass", key="news_force")

            if st.button("◈ Fetch Intelligence", key="news_fetch_btn"):
                needs_fetch = force_refresh or news_is_stale(st.session_state) or not is_done(st.session_state, "news_done")
                if needs_fetch:
                    try:
                        with st.spinner("Aggregating RSS feeds..."):
                            items = fetch_news(keywords=keywords, sources=selected_sources)
                        st.session_state["news_items"] = items
                        st.session_state["news_last_fetch"] = datetime.now(timezone.utc)
                        complete(st.session_state, "news_done")
                    except Exception as exc:
                        category = classify_error(exc)
                        st.session_state["last_error"] = f"[{category}] Intelligence fetch fault."
                        logger.exception(f"News fetch failed [{category}]")

            if st.session_state.get("news_items"):
                visible = [item for item in st.session_state["news_items"] if item.source in selected_sources]
                st.markdown(f'<div class="obs-micro" style="margin: 12px 0 4px;">{len(visible)} SIGNALS CAPTURED · LAST SYNC {st.session_state.get("news_last_fetch")}</div>', unsafe_allow_html=True)
                for item in visible[:25]:
                    st.markdown(f"**{item.title}** — `{item.source}` · {item.published:%Y-%m-%d %H:%M} UTC")
                    if item.summary: st.caption(item.summary)
                    st.caption(item.url)

                if st.button("◈ Synthesize AI Digest", key="ai_digest_btn"):
                    if not is_done(st.session_state, "ai_news_done"):
                        try:
                            with st.spinner("Synthesizing intelligence digest..."):
                                digest = generate_news_digest(st.session_state["news_items"])
                                st.session_state["ai_news_digest"] = digest
                                complete(st.session_state, "ai_news_done")
                        except Exception as exc:
                            category = classify_error(exc)
                            st.session_state["last_error"] = f"[{category}] AI digest fault."
                            logger.exception(f"AI digest failed [{category}]")

                if st.session_state.get("ai_news_digest"):
                    digest = st.session_state["ai_news_digest"]
                    st.markdown('<div class="obs-micro" style="margin: 16px 0 4px;">Executive Digest Synthesis</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="obs-card indigo"><div class="obs-kpi-label">Strategic Headline</div><div style="font-size: 16px; font-weight: 600; color: {theme.DESIGN_TOKENS["text_1"]}; line-height: 1.4;">{digest.headline_synthesis}</div></div>', unsafe_allow_html=True)
                    st.markdown("**Primary Disruption Vectors:**")
                    for d in digest.top_disruptions: st.markdown(f"- {d}")
                    st.markdown(f"**Supply Chain Impact Assessment:** {digest.supply_chain_impact}")
                    st.caption(f"Model Confidence: {digest.confidence:.2f}")

        with tab_weather:
            st.markdown('<div class="obs-micro">Environmental Risk Monitor</div>', unsafe_allow_html=True)
            pipeline_df = st.session_state.get("validated_df")
            if pipeline_df is None:
                st.markdown('<div class="obs-empty">◈ · INITIALIZE DATA PIPELINE TO ACCESS GEO-COORDINATES</div>', unsafe_allow_html=True)
            else:
                supplier_rows = pipeline_df.select(["supplier_id", "supplier_name", "latitude", "longitude"]).to_dicts()
                supplier_map = {f"{row['supplier_id']} · {row['supplier_name']}": row for row in supplier_rows}
                choice = st.selectbox("Select Entity Location", options=list(supplier_map.keys()), key="weather_supplier")

                if st.button("◈ Fetch Environmental Data", key="weather_fetch_btn"):
                    row = supplier_map[choice]
                    wkey = make_weather_key(st.session_state, row["supplier_id"])
                    if st.session_state.get("weather_key") != wkey or not is_done(st.session_state, "weather_done"):
                        try:
                            with st.spinner("Querying Open-Meteo..."):
                                report = fetch_weather(row["latitude"], row["longitude"])
                            st.session_state["weather_report"] = report
                            st.session_state["weather_key"] = wkey
                            complete(st.session_state, "weather_done")
                        except Exception as exc:
                            category = classify_error(exc)
                            st.session_state["last_error"] = f"[{category}] Environmental data fault."
                            logger.exception(f"Weather fetch failed [{category}]")

                report = st.session_state.get("weather_report")
                if report is not None:
                    w1, w2, w3, w4 = st.columns(4)
                    risk_map = {"LOW": "risk_low", "MODERATE": "risk_medium", "HIGH": "risk_high", "SEVERE": "risk_critical"}
                    with w1: st.markdown(theme.kpi_card("Temperature", f"{report.temperature_c:.1f}°C", accent="cyan"), unsafe_allow_html=True)
                    with w2: st.markdown(theme.kpi_card("Wind Velocity", f"{report.wind_kmh:.0f} km/h", accent="indigo"), unsafe_allow_html=True)
                    with w3: st.markdown(theme.kpi_card("Precipitation Prob", f"{report.precip_prob_pct:.0f}%", accent="indigo"), unsafe_allow_html=True)
                    with w4: st.markdown(theme.kpi_card("Shipping Risk", report.risk_level.value, accent=risk_map.get(report.risk_level.value, "risk_low")), unsafe_allow_html=True)
                    st.caption(f"Condition: {report.condition} @ ({report.latitude:.2f}, {report.longitude:.2f})")

        with tab_reports:
            st.markdown('<div class="obs-micro">Executive Briefing Outputs</div>', unsafe_allow_html=True)
            if not is_done(st.session_state, "scoring_done"):
                st.markdown('<div class="obs-empty">◈ · EXECUTE SCENARIO TO GENERATE BRIEFING DOCUMENTS</div>', unsafe_allow_html=True)
            else:
                scored_df = st.session_state["scored_df"]
                scenario_cfg = st.session_state["scenario_config"]
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown('<div class="obs-card"><div class="obs-kpi-label">PDF · Executive Summary</div><div style="font-size: 13px; color: #94A3B8; margin-top: 8px;">FPDF2 · Print-optimized board briefing</div></div>', unsafe_allow_html=True)
                    if st.session_state.get("report_pdf_bytes") is None:
                        if st.button("◈ Render PDF", key="render_pdf"):
                            try:
                                with st.spinner("Rendering FPDF2..."):
                                    st.session_state["report_pdf_bytes"] = render_pdf_report(scored_df, st.session_state.get("ai_narratives", {}), scenario_cfg.scenario_name)
                            except Exception as exc:
                                st.session_state["last_error"] = f"[{classify_error(exc)}] PDF render fault."
                    if st.session_state.get("report_pdf_bytes") is not None:
                        st.download_button("◈ Download PDF", st.session_state["report_pdf_bytes"], file_name=f"risk_briefing_{scenario_cfg.scenario_name[:20]}.pdf", mime="application/pdf", key="download_pdf")

                with c2:
                    st.markdown('<div class="obs-card indigo"><div class="obs-kpi-label">HTML · Interactive Briefing</div><div style="font-size: 13px; color: #94A3B8; margin-top: 8px;">Jinja2 + Plotly · Embeddable digital report</div></div>', unsafe_allow_html=True)
                    if st.session_state.get("report_html_str") is None:
                        if st.button("◈ Render HTML", key="render_html"):
                            try:
                                with st.spinner("Rendering HTML briefing..."):
                                    st.session_state["report_html_str"] = render_html_report(scored_df, st.session_state.get("ai_narratives", {}), scenario_cfg.scenario_name)
                            except Exception as exc:
                                st.session_state["last_error"] = f"[{classify_error(exc)}] HTML render fault."
                    if st.session_state.get("report_html_str") is not None:
                        st.download_button("◈ Download HTML", st.session_state["report_html_str"], file_name=f"risk_briefing_{scenario_cfg.scenario_name[:20]}.html", mime="text/html", key="download_html")
