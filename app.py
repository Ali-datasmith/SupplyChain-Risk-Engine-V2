"""Supply Chain Risk Engine V2 — Premium B2B Command Center."""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
    news_is_stale, register_upload,
)
from telemetry.logger import configure_logging, logger
from telemetry.streamlit_handler import StreamlitLogHandler

MAX_UPLOAD_BYTES = 20_000_000

try:
    st.set_page_config(page_title="Supply Chain Risk Engine V2", layout="wide", page_icon="◆")
except Exception:
    pass

init_session_state(st.session_state)
configure_logging()

log_handler = StreamlitLogHandler(buffer=st.session_state["log_buffer"])
log_handler.attach()


def _md_neutral(text: str) -> str:
    """Neutralize markdown link/image syntax from untrusted external text."""
    return (text or "").replace("<", "").replace(">", "").replace("](", "] (")


def _safe_url(url: str) -> bool:
    return url.startswith("https://") or url.startswith("http://")


st.markdown(theme.inject_theme_css(), unsafe_allow_html=True)

degraded = bool(st.session_state.get("last_error"))
st.markdown(theme.brand_bar(), unsafe_allow_html=True)
st.markdown(theme.ops_strip(status="DEGRADED" if degraded else "OPERATIONAL"), unsafe_allow_html=True)

if st.session_state["last_error"]:
    st.error(st.session_state["last_error"])
    st.session_state["last_error"] = None

with st.sidebar:
    log_handler.render()

st.markdown('<div class="obs-micro">Data Ingestion</div>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload supplier CSV to begin analysis", type=["csv"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file is None:
    st.markdown('<div class="obs-empty">Upload a supplier CSV to initialize the risk engine</div>', unsafe_allow_html=True)
elif uploaded_file.size > MAX_UPLOAD_BYTES:
    st.error("Payload exceeds the 20 MB free-tier ingestion ceiling. Split the batch and re-upload.")
    st.stop()
else:
    upload_bytes = uploaded_file.getvalue()
    is_new_upload = register_upload(st.session_state, upload_bytes)

    if is_new_upload:
        st.session_state.pop("map_obj", None)
        logger.bind(request_id=st.session_state["raw_upload_hash"][:8]).info("New upload registered.")

    if not is_done(st.session_state, "validation_done"):
        try:
            with st.spinner("Sanitizing and validating schema..."):
                validated_df = ingest_supplier_csv(upload_bytes)
                st.session_state["validated_df"] = validated_df
                complete(st.session_state, "validation_done")
                logger.info(f"Validation complete: {validated_df.height} rows")
                st.success("Data payload sanitized and validated.")
        except IngestionError as exc:
            category = classify_error(exc)
            st.session_state["validation_errors"] = exc.failure_cases
            st.session_state["last_error"] = f"[{category}] Validation rejected the payload."
            logger.error(f"Validation failed [{category}]: {exc}")
            st.stop()
        except Exception as exc:
            category = classify_error(exc)
            st.session_state["last_error"] = f"[{category}] Ingestion fault."
            logger.exception(f"Ingestion failed [{category}]")
            st.stop()

    if is_done(st.session_state, "validation_done"):
        tab_overview, tab_map, tab_news, tab_weather, tab_reports = st.tabs(
            ["Risk Overview", "Global Map", "Intel Feed", "Weather", "Reports"]
        )

        # ══════════ RISK OVERVIEW ══════════
        with tab_overview:
            st.markdown('<div class="obs-micro">Scenario Configuration</div>', unsafe_allow_html=True)
            existing_config = st.session_state.get("scenario_config")
            default_name = existing_config.scenario_name if existing_config else "Baseline"
            default_regions = existing_config.regions if existing_config else ["EMEA", "APAC", "NA", "LATAM"]
            default_min = existing_config.min_risk_threshold if existing_config else 0.0
            default_max = existing_config.max_risk_threshold if existing_config else 1.0
            weighting_options = list(RiskWeighting)
            default_weighting_index = weighting_options.index(existing_config.weighting) if existing_config else 0

            with st.container(border=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    scenario_name = st.text_input("Scenario Name", value=default_name, key="scenario_name")
                    regions = st.multiselect("Target Regions", ["EMEA", "APAC", "NA", "LATAM"], default=default_regions, key="regions")
                with c2:
                    min_risk = st.slider("Min Risk Threshold", 0.0, 1.0, default_min, key="min_risk")
                    max_risk = st.slider("Max Risk Threshold", 0.0, 1.0, default_max, key="max_risk")
                with c3:
                    weighting = st.selectbox("Weighting Model", weighting_options, index=default_weighting_index, format_func=lambda item: item.value.replace("_", " ").title(), key="weighting")
                    if st.button("Execute Risk Scenario", key="apply_scenario", type="primary"):
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
                            st.session_state["last_error"] = f"[{category}] Invalid scenario."
                            logger.error(f"Invalid scenario [{category}]: {exc}")

            if st.session_state.get("scenario_config") is not None and not is_done(st.session_state, "scoring_done"):
                try:
                    with st.spinner("Vectorizing and scoring suppliers..."):
                        scored_df = score_suppliers(st.session_state["validated_df"], st.session_state["scenario_config"])
                        st.session_state["scored_df"] = scored_df
                        complete(st.session_state, "scoring_done")
                        logger.info(f"Scoring complete: {scored_df.height} suppliers")
                except Exception as exc:
                    category = classify_error(exc)
                    st.session_state["last_error"] = f"[{category}] Scoring fault."
                    logger.exception(f"Scoring failed [{category}]")

            if is_done(st.session_state, "scoring_done"):
                scored_df = st.session_state["scored_df"]

                st.markdown('<div class="obs-micro" style="margin-top:18px;">Key Performance Indicators</div>', unsafe_allow_html=True)
                total_suppliers = scored_df.height
                avg_risk = float(scored_df["composite_risk"].mean()) if "composite_risk" in scored_df.columns else 0.0
                high_risk = scored_df.filter(pl.col("composite_risk") >= 0.7).height if "composite_risk" in scored_df.columns else 0
                critical_count = scored_df.filter(pl.col("composite_risk") >= 0.85).height if "composite_risk" in scored_df.columns else 0

                k1, k2, k3, k4 = st.columns(4)
                with k1: st.metric("Total Suppliers", f"{total_suppliers:,}")
                with k2: st.metric("Avg Risk Index", f"{avg_risk:.3f}")
                with k3: st.metric("High Risk", f"{high_risk:,}")
                with k4: st.metric("Critical", f"{critical_count:,}")
                st.caption("Bands: HIGH ≥ 0.70 · CRITICAL ≥ 0.85 · deltas omitted (no fabricated trends)")

                if "region" in scored_df.columns and "composite_risk" in scored_df.columns:
                    st.markdown('<div class="obs-micro" style="margin-top:18px;">Regional Threat Landscape</div>', unsafe_allow_html=True)
                    region_agg = (
                        scored_df.group_by("region")
                        .agg([pl.col("composite_risk").mean().alias("avg_risk"), pl.col("supplier_id").count().alias("count")])
                        .sort("avg_risk", descending=True)
                    )
                    fig = px.bar(
                        region_agg.to_pandas(),
                        x="region", y="avg_risk", color="avg_risk",
                        color_discrete_sequence=[theme.DESIGN_TOKENS["accent"], theme.DESIGN_TOKENS["accent_2"]],
                        custom_data=["count"],
                    )
                    fig.update_layout(
                        title="Risk by region", xaxis_title="Region", yaxis_title="Avg Risk", showlegend=False,
                        **theme.get_plotly_layout(),
                    )
                    fig.update_traces(
                        hovertemplate="<b>%{x}</b><br>Risk: %{y:.3f}<br>Count: %{customdata[0]}<extra></extra>",
                        marker_line_width=0,
                    )
                    st.plotly_chart(fig, use_container_width=True)

                st.markdown('<div class="obs-micro" style="margin-top:18px;">Supplier Risk Ledger</div>', unsafe_allow_html=True)
                display_df = scored_df.sort("composite_risk", descending=True).select(
                    ["supplier_id", "supplier_name", "region", "tier", "composite_risk", "annual_spend_usd"]
                )
                st.dataframe(
                    display_df, use_container_width=True, hide_index=True, height=420,
                    column_config={
                        "supplier_id": st.column_config.TextColumn("ID", width="small"),
                        "supplier_name": st.column_config.TextColumn("Name", width="medium"),
                        "region": st.column_config.TextColumn("Region", width="small"),
                        "tier": st.column_config.NumberColumn("Tier", width="small"),
                        "composite_risk": st.column_config.ProgressColumn("Risk", min_value=0.0, max_value=1.0, format="%.3f", width="small"),
                        "annual_spend_usd": st.column_config.NumberColumn("Annual spend", format="$%s", width="small"),
                    },
                )

                if st.session_state["scenario_config"].include_ai_narrative:
                    st.markdown('<div class="obs-micro" style="margin-top:18px;">AI Risk Narratives</div>', unsafe_allow_html=True)
                    if not is_done(st.session_state, "ai_generation_done"):
                        try:
                            with st.spinner("Generating AI executive briefings..."):
                                narratives = generate_narratives(scored_df.head(10).to_dicts())
                                st.session_state["ai_narratives"] = narratives
                                st.session_state["ai_call_count"] += 1
                                complete(st.session_state, "ai_generation_done")
                                logger.info(f"AI narratives generated: {len(narratives)}")
                        except Exception as exc:
                            category = classify_error(exc)
                            st.session_state["last_error"] = f"[{category}] AI synthesis fault."
                            logger.exception(f"AI generation failed [{category}]")

                    for supplier_id, narrative in (st.session_state.get("ai_narratives") or {}).items():
                        with st.expander(f"{narrative.supplier_name} · {supplier_id}"):
                            st.markdown(theme.status_pill(narrative.overall_risk), unsafe_allow_html=True)
                            st.markdown(f"**Key Risks:** {_md_neutral(', '.join(narrative.key_risks))}")
                            st.markdown(f"**Recommendation:** {_md_neutral(narrative.recommendation)}")
                            st.caption(f"Model Confidence: {narrative.confidence:.2f}")

        # ══════════ GLOBAL MAP ══════════
        with tab_map:
            st.markdown('<div class="obs-micro">Global Supplier Network</div>', unsafe_allow_html=True)
            if not is_done(st.session_state, "scoring_done"):
                st.markdown('<div class="obs-empty">Execute a scenario to render the geospatial map</div>', unsafe_allow_html=True)
            else:
                scored_df = st.session_state["scored_df"]
                band_col = (
                    pl.when(pl.col("composite_risk") >= 0.85).then(pl.lit("CRITICAL"))
                    .when(pl.col("composite_risk") >= 0.70).then(pl.lit("HIGH"))
                    .when(pl.col("composite_risk") >= 0.40).then(pl.lit("MEDIUM"))
                    .otherwise(pl.lit("LOW"))
                    .alias("band")
                )
                counts = {
                    row["band"]: row["n"]
                    for row in scored_df.with_columns(band_col).group_by("band").len().to_dicts()
                    for row in [row]
                } if scored_df.height else {}
                counts = {r["band"]: r["n"] for r in scored_df.with_columns(band_col).group_by("band").len().to_dicts()}
                st.markdown(theme.legend_html(counts), unsafe_allow_html=True)
                st.caption("Marker radius scales with composite risk · hover for entity detail")

                if not is_done(st.session_state, "map_render_done") or "map_obj" not in st.session_state:
                    try:
                        with st.spinner("Compiling geospatial coordinates..."):
                            st.session_state["map_obj"] = build_map(scored_df, st.session_state["scenario_config"])
                            complete(st.session_state, "map_render_done")
                    except Exception as exc:
                        category = classify_error(exc)
                        st.session_state["last_error"] = f"[{category}] Map render fault."
                        logger.exception(f"Map rendering failed [{category}]")

                if "map_obj" in st.session_state:
                    render_in_streamlit(st.session_state["map_obj"])

        # ══════════ INTEL FEED ══════════
        with tab_news:
            st.markdown('<div class="obs-micro">Live Threat Intelligence Feed</div>', unsafe_allow_html=True)
            keywords = st.text_input("Filter Keywords", value="port, strike, disruption, shortage", key="news_keywords")
            selected_sources = st.multiselect("Target Sources", options=list(RSS_SOURCES.keys()), default=list(RSS_SOURCES.keys()), key="news_sources")
            force_refresh = st.checkbox("Force Refresh", key="news_force")

            if st.button("Fetch Intel", key="news_fetch_btn"):
                needs_fetch = force_refresh or news_is_stale(st.session_state) or not is_done(st.session_state, "news_done")
                if needs_fetch:
                    try:
                        with st.spinner("Scraping RSS feeds..."):
                            items = fetch_news(keywords=keywords, sources=selected_sources)
                        st.session_state["news_items"] = items
                        st.session_state["news_last_fetch"] = datetime.now(timezone.utc)
                        complete(st.session_state, "news_done")
                        logger.bind(source="rss").info(f"News fetch complete: {len(items)} items")
                    except Exception as exc:
                        category = classify_error(exc)
                        st.session_state["last_error"] = f"[{category}] News fetch fault."
                        logger.exception(f"News fetch failed [{category}]")

            if st.session_state.get("news_items"):
                visible = [i for i in st.session_state["news_items"] if i.source in selected_sources]
                st.caption(f"{len(visible)} articles · last update {st.session_state.get('news_last_fetch')} UTC")
                with st.container(border=True):
                    for item in visible[:25]:
                        st.markdown(f"**{_md_neutral(item.title)}**")
                        st.caption(f"{item.source} · {item.published:%Y-%m-%d %H:%M} UTC")
                        if item.summary:
                            st.caption(_md_neutral(item.summary))
                        if _safe_url(item.url):
                            st.caption(f"Source: {item.url}")
                        st.divider()

                if st.button("Synthesize AI Digest", key="ai_digest_btn"):
                    if not is_done(st.session_state, "ai_news_done"):
                        try:
                            with st.spinner("Synthesizing AI summary..."):
                                st.session_state["ai_news_digest"] = generate_news_digest(st.session_state["news_items"])
                                complete(st.session_state, "ai_news_done")
                        except Exception as exc:
                            category = classify_error(exc)
                            st.session_state["last_error"] = f"[{category}] AI digest fault."
                            logger.exception(f"AI digest failed [{category}]")

                if st.session_state.get("ai_news_digest"):
                    digest = st.session_state["ai_news_digest"]
                    st.markdown('<div class="obs-micro" style="margin-top:14px;">AI Executive Summary</div>', unsafe_allow_html=True)
                    with st.container(border=True):
                        st.markdown(f"**Headline:** {_md_neutral(digest.headline_synthesis)}")
                        st.markdown("**Top Disruptions:**")
                        for d in digest.top_disruptions:
                            st.markdown(f"- {_md_neutral(d)}")
                        st.markdown(f"**Supply Chain Impact:** {_md_neutral(digest.supply_chain_impact)}")
                        st.caption(f"Confidence: {digest.confidence:.2f}")

        # ══════════ WEATHER ══════════
        with tab_weather:
            st.markdown('<div class="obs-micro">Environmental Threat Monitoring</div>', unsafe_allow_html=True)
            pipeline_df = st.session_state.get("validated_df")
            if pipeline_df is None:
                st.markdown('<div class="obs-empty">Upload a CSV to monitor weather conditions</div>', unsafe_allow_html=True)
            else:
                supplier_rows = pipeline_df.select(["supplier_id", "supplier_name", "latitude", "longitude"]).to_dicts()
                supplier_map = {f"{r['supplier_id']} · {r['supplier_name']}": r for r in supplier_rows}
                choice = st.selectbox("Select Supplier Node", options=list(supplier_map.keys()), key="weather_supplier")

                if st.button("Fetch Forecast", key="weather_fetch_btn"):
                    row = supplier_map[choice]
                    wkey = make_weather_key(st.session_state, row["supplier_id"])
                    if st.session_state.get("weather_key") != wkey or not is_done(st.session_state, "weather_done"):
                        try:
                            with st.spinner("Querying Open-Meteo..."):
                                report = fetch_weather(row["latitude"], row["longitude"])
                            st.session_state["weather_report"] = report
                            st.session_state["weather_key"] = wkey
                            complete(st.session_state, "weather_done")
                            logger.bind(source="open-meteo").info("Weather fetch complete")
                        except Exception as exc:
                            category = classify_error(exc)
                            st.session_state["last_error"] = f"[{category}] Weather fault."
                            logger.exception(f"Weather fetch failed [{category}]")

                report = st.session_state.get("weather_report")
                if report is not None:
                    w1, w2, w3, w4 = st.columns(4)
                    with w1: st.metric("Temperature", f"{report.temperature_c:.1f}°C")
                    with w2: st.metric("Wind Speed", f"{report.wind_kmh:.0f} km/h")
                    with w3: st.metric("Precipitation", f"{report.precip_prob_pct:.0f}%")
                    with w4: st.metric("Shipping Risk", report.risk_level.value)
                    st.caption(f"Condition: {report.condition} @ ({report.latitude:.2f}, {report.longitude:.2f})")

        # ══════════ REPORTS ══════════
        with tab_reports:
            st.markdown('<div class="obs-micro">Board-Ready Deliverables</div>', unsafe_allow_html=True)
            if not is_done(st.session_state, "scoring_done"):
                st.markdown('<div class="obs-empty">Execute a scenario to generate reports</div>', unsafe_allow_html=True)
            else:
                scored_df = st.session_state["scored_df"]
                scenario_cfg = st.session_state["scenario_config"]
                c1, c2 = st.columns(2)

                with c1:
                    st.markdown("#### PDF Executive Briefing")
                    if st.session_state.get("report_pdf_bytes") is None:
                        if st.button("Generate PDF", key="render_pdf"):
                            try:
                                with st.spinner("Rendering PDF..."):
                                    st.session_state["report_pdf_bytes"] = render_pdf_report(
                                        scored_df,
                                        st.session_state.get("ai_narratives", {}),
                                        scenario_cfg.scenario_name,
                                        scenario_config=scenario_cfg,
                                    )
                                    logger.info("PDF generated")
                            except Exception as exc:
                                st.session_state["last_error"] = f"[{classify_error(exc)}] PDF fault."
                                logger.exception(f"PDF failed [{classify_error(exc)}]")
                    if st.session_state.get("report_pdf_bytes") is not None:
                        st.download_button("Download PDF Report", st.session_state["report_pdf_bytes"], file_name="risk_report.pdf", mime="application/pdf", key="download_pdf")

                with c2:
                    st.markdown("#### Interactive HTML Briefing")
                    if st.session_state.get("report_html_str") is None:
                        if st.button("Generate HTML", key="render_html"):
                            try:
                                with st.spinner("Compiling HTML..."):
                                    st.session_state["report_html_str"] = render_html_report(
                                        scored_df, st.session_state.get("ai_narratives", {}), scenario_cfg.scenario_name
                                    )
                                    logger.info("HTML generated")
                            except Exception as exc:
                                st.session_state["last_error"] = f"[{classify_error(exc)}] HTML fault."
                                logger.exception(f"HTML failed [{classify_error(exc)}]")
                    if st.session_state.get("report_html_str") is not None:
                        st.download_button("Download HTML Report", st.session_state["report_html_str"], file_name="risk_report.html", mime="text/html", key="download_html")
