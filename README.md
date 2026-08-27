# ⚡ Supply Chain Risk Engine V2

> **Enterprise-Grade Supply Chain Intelligence & Risk Command Center**

![Python](https://img.shields.io/badge/Python-3.12%20|%203.13-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-FF4B4B?style=flat-square&logo=streamlit)
![CI](https://github.com/Ali-datasmith/SupplyChain-Risk-Engine-V2/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

## 🚀 Overview
The **Supply Chain Risk Engine V2** is a high-performance, B2B SaaS-grade application designed to ingest, validate, and score massive supply chain datasets in real-time. Powered by **Polars**, **DuckDB**, and **Google GenAI**, it provides executive risk briefings, geospatial threat mapping, and live external intelligence (RSS & Weather) in a premium command-center interface.

![Premium B2B Dashboard](https://via.placeholder.com/1200x600/0B1220/22D3EE?text=Premium+Glassmorphism+Command+Center+UI)

## ✨ Key Features
- **Premium B2B UI**: Dark mode, glassmorphism design system, neon critical alerts, and real-time telemetry.
- **Lazy Execution Engine**: Vectorized risk scoring using `polars` and `duckdb` for sub-second 50k+ row joins.
- **Typed AI Narratives**: Google GenAI integration with Pydantic V2 for structured, board-ready risk assessments.
- **Resilient API Layer**: `httpx` + `tenacity` with exponential backoff for live RSS & weather feeds.
- **Pandera Validation Gate**: Strict schema enforcement before any data touches the engine.
- **Automated Reporting**: Dual PDF and interactive HTML report generation via Jinja2.

## 🛠️ Tech Stack
- **Compute & Data**: Polars, DuckDB, Pandera
- **Frontend**: Streamlit, Plotly, PyDeck, Pure CSS Glassmorphism
- **AI & GenAI**: Google GenAI, Pydantic V2
- **Resilience**: HTTPX, Tenacity
- **CI/CD**: GitHub Actions (Python 3.12/3.13 Matrix)

## ⚡ Architecture Diagram
```text
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  CSV Ingestion  │ ──▶ │  Pandera Schema  │ ──▶ │  Polars / DuckDB│
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Executive PDF  │ ◀── │  Risk Scoring    │ ◀── │  Scenario Config│
└─────────────────┘     └──────────────────┘     └─────────────────┘
        ▲                        │
        │                        ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  GenAI (Gemini) │ ◀── │ Pydantic V2 JSON │ ◀── │  Supplier Nodes │
└─────────────────┘     └──────────────────┘     └─────────────────┘

# Clone the repository
git clone https://github.com/Ali-datasmith/SupplyChain-Risk-Engine-V2.git
cd SupplyChain-Risk-Engine-V2

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py

# Run the test suite
pytest -q
