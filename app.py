"""
Supply Chain Risk Engine V2.1 - Streamlit entrypoint.

Single-Path Guard wiring:
upload -> validate -> score -> map -> AI -> reports
plus V2.1 tabs: Intelligence Feed (RSS + AI digest) and Weather Monitor.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import polars as pl
import streamlit as st

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
    complete,
    init_session_state,
    is_done,
    make_weather_key,
    news_is_stale,
    register_upload,
    scenario_key,
)
from telemetry.logger import configure_logging, logger
from telemetry.streamlit_handler import StreamlitLogHandler

try:
    st.set_page_config(page_title="Supply Chain Risk Engine V2.1", layout="wide")
except Exception:
    pass

init_session_state(st.session_state)
configure_logging()

log_handler = StreamlitLogHandler(buffer=st.session_state["log_buffer"])
log_handler.attach()
log_handler.render()

if st.session_state["last_error"]:
    st.error(st.session_state["last_error"])
    st.session_state["last_error"] = None

st.title("Supply Chain Risk Engine V2.1")

tab_pipeline, tab_intel, tab_weather = st.tabs(
    ["Risk Pipeline", "Intelligence Feed", "Weather Monitor"]
)

# ═══════════════════════════ RISK PIPELINE ═══════════════════════════
with tab_pipeline:
    uploaded_file = st.file_uploader("Upload Supplier CSV", type=["csv"])

    if uploaded_file is None:
        st.info("Upload a supplier CSV to begin.")
    else:
        upload_bytes = uploaded_file.getvalue()
        is_new_upload = register_upload(st.session_state, upload_bytes)

        if is_new_upload:
            st.session_state.pop("map_obj", None)
            logger.bind(request_id=st.session_state["raw_upload_hash"][:8]).info(
                "New upload registered; downstream stages invalidated."
            )

        if not is_done(st.session_state, "validation_done"):
            try:
                with st.spinner("Validating supplier data..."):
                    validated_df = ingest_supplier_csv(upload_bytes)
                    st.session_state["validated_df"] = validated_df
                    complete(st.session_state, "validation_done")
                    logger.info(f"Validation complete: {validated_df.height} rows")
            except IngestionError as exc:
                category = classify_error(exc)
                st.session_state["validation_errors"] = exc.failure_cases
                st.session_state["last_error"] = f"[{category}] Supplier validation failed: {exc}"
                logger.error(f"Validation failed [{category}]: {exc}")
                st.stop()
            except Exception as exc:
                category = classify_error(exc)
                st.session_state["last_error"] = f"[{category}] Ingestion failed: {exc}"
                logger.exception(f"Ingestion failed [{category}]")
                st.stop()

        if is_done(st.session_state, "validation_done"):
            validated_df = st.session_state["validated_df"]
            st.success(f"Validated {validated_df.height} suppliers")

            st.subheader("Scenario Configuration")
            existing_config = st.session_state.get("scenario_config")

            default_name = existing_config.scenario_name if existing_config else "Default Scenario"
            default_regions = (
                existing_config.regions if existing_config else ["EMEA", "APAC", "NA", "LATAM"]
            )
            default_min = existing_config.min_risk_threshold if existing_config else 0.0
            default_max = existing_config.max_risk_threshold if existing_config else 1.0

            weighting_options = list(RiskWeighting)
            default_weighting_index = (
                weighting_options.index(existing_config.weighting) if existing_config else 0
            )

            col1, col2 = st.columns(2)
            with col1:
                scenario_name = st.text_input("Scenario Name", value=default_name)
                regions = st.multiselect(
                    "Regions",
                    ["EMEA", "APAC", "NA", "LATAM"],
                    default=default_regions,
                )
            with col2:
                min_risk = st.slider("Min Risk Threshold", 0.0, 1.0, default_min)
                max_risk = st.slider("Max Risk Threshold", 0.0, 1.0, default_max)

            weighting = st.selectbox(
                "Risk Weighting",
                options=weighting_options,
                index=default_weighting_index,
                format_func=lambda item: item.value,
            )

            if st.button("Apply Scenario"):
                try:
                    config = ScenarioConfig(
                        scenario_name=scenario_name,
                        regions=regions,
                        min_risk_threshold=min_risk,
                        max_risk_threshold=max_risk,
                        weighting=weighting,
                    )

                    if existing_config != config:
                        st.session_state["scenario_config"] = config
                        st.session_state["scoring_done"] = False
                        st.session_state["ai_generation_done"] = False
                        st.session_state["ai_narratives"] = {}
                        st.session_state["report_pdf_bytes"] = None
                        st.session_state["report_html_str"] = None
                        st.session_state.pop("map_obj", None)
                        logger.info(f"Scenario applied: {config.scenario_name}")
                    else:
                        logger.info("Scenario unchanged; no downstream invalidation.")
                except Exception as exc:
                    category = classify_error(exc)
                    st.session_state["last_error"] = f"[{category}] Invalid scenario: {exc}"
                    logger.error(f"Invalid scenario [{category}]: {exc}")

            if st.session_state.get("scenario_config") is not None and not is_done(
                st.session_state, "scoring_done"
            ):
                try:
                    with st.spinner("Scoring suppliers..."):
                        scored_df = score_suppliers(validated_df, st.session_state["scenario_config"])
                        st.session_state["scored_df"] = scored_df
                        complete(st.session_state, "scoring_done")
                        logger.info(f"Scoring complete: {scored_df.height} suppliers")
                except Exception as exc:
                    category = classify_error(exc)
                    st.session_state["last_error"] = f"[{category}] Scoring failed: {exc}"
                    logger.exception(f"Scoring failed [{category}]")

            if is_done(st.session_state, "scoring_done"):
                scored_df = st.session_state["scored_df"]
                st.success(f"Scored {scored_df.height} suppliers")

                if not is_done(st.session_state, "map_render_done") or "map_obj" not in st.session_state:
                    try:
                        with st.spinner("Building map..."):
                            map_obj = build_map(scored_df, st.session_state["scenario_config"])
                            st.session_state["map_obj"] = map_obj
                            complete(st.session_state, "map_render_done")
                            logger.bind(scenario_key=scenario_key(st.session_state)[0]).info("Map built")
                    except Exception as exc:
                        category = classify_error(exc)
                        st.session_state["last_error"] = f"[{category}] Map rendering failed: {exc}"
                        logger.exception(f"Map rendering failed [{category}]")

                if "map_obj" in st.session_state:
                    st.subheader("Risk Map")
                    render_in_streamlit(st.session_state["map_obj"])

                if st.session_state["scenario_config"].include_ai_narrative and not is_done(
                    st.session_state, "ai_generation_done"
                ):
                    try:
                        with st.spinner("Generating AI narratives..."):
                            rows = scored_df.head(10).to_dicts()
                            narratives = generate_narratives(rows)
                            st.session_state["ai_narratives"] = narratives
                            st.session_state["ai_call_count"] += 1
                            complete(st.session_state, "ai_generation_done")
                            logger.info(f"AI narratives generated: {len(narratives)}")
                    except Exception as exc:
                        category = classify_error(exc)
                        st.session_state["last_error"] = f"[{category}] AI narrative generation failed: {exc}"
                        logger.exception(f"AI generation failed [{category}]")

                if st.session_state.get("ai_narratives"):
                    st.subheader("AI Risk Narratives")
                    for supplier_id, narrative in st.session_state["ai_narratives"].items():
                        with st.expander(f"{narrative.supplier_name} (ID: {supplier_id})"):
                            st.write(f"**Overall Risk:** {narrative.overall_risk.value}")
                            st.write(f"**Key Risks:** {', '.join(narrative.key_risks)}")
                            st.write(f"**Recommendation:** {narrative.recommendation}")
                            st.write(f"**Confidence:** {narrative.confidence:.2f}")

                st.subheader("Reports")
                report_col1, report_col2 = st.columns(2)

                with report_col1:
                    if st.session_state.get("report_pdf_bytes") is None:
                        if st.button("Generate PDF Report"):
                            try:
                                with st.spinner("Generating PDF..."):
                                    pdf_bytes = render_pdf_report(
                                        scored_df,
                                        st.session_state.get("ai_narratives", {}),
                                        st.session_state["scenario_config"].scenario_name,
                                    )
                                    st.session_state["report_pdf_bytes"] = pdf_bytes
                                    logger.info("PDF report generated")
                            except Exception as exc:
                                category = classify_error(exc)
                                st.session_state["last_error"] = f"[{category}] PDF generation failed: {exc}"
                                logger.exception(f"PDF generation failed [{category}]")

                    if st.session_state.get("report_pdf_bytes") is not None:
                        st.download_button(
                            "Download PDF",
                            st.session_state["report_pdf_bytes"],
                            file_name="risk_report.pdf",
                            mime="application/pdf",
                        )

                with report_col2:
                    if st.session_state.get("report_html_str") is None:
                        if st.button("Generate HTML Report"):
                            try:
                                with st.spinner("Generating HTML..."):
                                    html_str = render_html_report(
                                        scored_df,
                                        st.session_state.get("ai_narratives", {}),
                                        st.session_state["scenario_config"].scenario_name,
                                    )
                                    st.session_state["report_html_str"] = html_str
                                    logger.info("HTML report generated")
                            except Exception as exc:
                                category = classify_error(exc)
                                st.session_state["last_error"] = f"[{category}] HTML generation failed: {exc}"
                                logger.exception(f"HTML generation failed [{category}]")

                    if st.session_state.get("report_html_str") is not None:
                        st.download_button(
                            "Download HTML",
                            st.session_state["report_html_str"],
                            file_name="risk_report.html",
                            mime="text/html",
                        )

# ═══════════════════════════ INTELLIGENCE FEED ═══════════════════════════
with tab_intel:
    st.subheader("Live Intelligence Feed")

    keywords = st.text_input(
        "Keyword filter (comma-separated)",
        value="port, strike, disruption, shortage",
        key="news_keywords",
    )
    selected_sources = st.multiselect(
        "Sources",
        options=list(RSS_SOURCES.keys()),
        default=list(RSS_SOURCES.keys()),
        key="news_sources",
    )
    force_refresh = st.checkbox("Force refresh", key="news_force")

    if st.button("Fetch News", key="news_fetch_btn"):
        needs_fetch = (
            force_refresh
            or news_is_stale(st.session_state)
            or not is_done(st.session_state, "news_done")
        )

        if needs_fetch:
            try:
                with st.spinner("Fetching RSS feeds..."):
                    items = fetch_news(keywords=keywords, sources=selected_sources)
                st.session_state["news_items"] = items
                st.session_state["news_last_fetch"] = datetime.now(timezone.utc)
                complete(st.session_state, "news_done")
                logger.bind(source="rss").info(f"News fetch complete: {len(items)} items")
            except Exception as exc:
                category = classify_error(exc)
                st.session_state["last_error"] = f"[{category}] News fetch failed: {exc}"
                logger.exception(f"News fetch failed [{category}]")
        else:
            logger.bind(source="rss").info("News cache fresh; skipping fetch.")

    if st.session_state.get("news_items"):
        visible = [
            item for item in st.session_state["news_items"] if item.source in selected_sources
        ]
        st.caption(
            f"{len(visible)} items | last fetch: {st.session_state.get('news_last_fetch')}"
        )

        for item in visible[:25]:
            st.markdown(f"**{item.title}** — {item.source} ({item.published:%Y-%m-%d %H:%M} UTC)")
            if item.summary:
                st.caption(item.summary)
            st.caption(item.url)

        if st.button("Generate AI Digest", key="ai_digest_btn"):
            if not is_done(st.session_state, "ai_news_done"):
                try:
                    with st.spinner("Synthesizing AI digest..."):
                        digest = generate_news_digest(st.session_state["news_items"])
                        st.session_state["ai_news_digest"] = digest
                        complete(st.session_state, "ai_news_done")
                        logger.bind(source="genai").info("AI news digest generated")
                except Exception as exc:
                    category = classify_error(exc)
                    st.session_state["last_error"] = f"[{category}] AI digest failed: {exc}"
                    logger.exception(f"AI digest failed [{category}]")

        if st.session_state.get("ai_news_digest"):
            digest = st.session_state["ai_news_digest"]
            st.subheader("AI News Digest")
            st.markdown(f"**{digest.headline_synthesis}**")
            st.markdown("**Top disruptions:**")
            for disruption in digest.top_disruptions:
                st.markdown(f"- {disruption}")
            st.markdown(f"**Supply chain impact:** {digest.supply_chain_impact}")
            st.caption(f"Confidence: {digest.confidence:.2f}")

# ═══════════════════════════ WEATHER MONITOR ═══════════════════════════
with tab_weather:
    st.subheader("Port Weather Monitor")

    pipeline_df = st.session_state.get("validated_df")

    if pipeline_df is None:
        st.info("Validate a supplier CSV in the Risk Pipeline tab first.")
    else:
        supplier_rows = (
            pipeline_df.select(["supplier_id", "supplier_name", "latitude", "longitude"])
            .to_dicts()
        )
        supplier_map = {
            f"{row['supplier_id']} — {row['supplier_name']}": row for row in supplier_rows
        }

        choice = st.selectbox(
            "Supplier location",
            options=list(supplier_map.keys()),
            key="weather_supplier",
        )

        if st.button("Fetch Weather", key="weather_fetch_btn"):
            row = supplier_map[choice]
            wkey = make_weather_key(st.session_state, row["supplier_id"])

            if st.session_state.get("weather_key") != wkey or not is_done(
                st.session_state, "weather_done"
            ):
                try:
                    with st.spinner("Fetching Open-Meteo forecast..."):
                        report = fetch_weather(row["latitude"], row["longitude"])
                    st.session_state["weather_report"] = report
                    st.session_state["weather_key"] = wkey
                    complete(st.session_state, "weather_done")
                    logger.bind(source="open-meteo").info("Weather fetch complete")
                except Exception as exc:
                    category = classify_error(exc)
                    st.session_state["last_error"] = f"[{category}] Weather fetch failed: {exc}"
                    logger.exception(f"Weather fetch failed [{category}]")

        report = st.session_state.get("weather_report")
        if report is not None:
            w1, w2, w3, w4 = st.columns(4)
            w1.metric("Temperature", f"{report.temperature_c:.1f}°C")
            w2.metric("Wind", f"{report.wind_kmh:.0f} km/h")
            w3.metric("Precipitation", f"{report.precip_prob_pct:.0f}%")
            w4.metric("Shipping Risk", report.risk_level.value)
            st.caption(
                f"Condition: {report.condition} @ ({report.latitude:.2f}, {report.longitude:.2f})"
            )
