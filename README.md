# ⚡ Supply Chain Risk Engine V2

> **Enterprise-Grade Supply Chain Risk Engine & Real-Time Intelligence Command Center**

![Python](https://img.shields.io/badge/Python-3.12%20|%203.13-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-FF4B4B?style=flat-square&logo=streamlit)
![CI](https://github.com/Ali-datasmith/SupplyChain-Risk-Engine-V2/actions/workflows/ci.yml/badge.svg)
![CodeQL](https://github.com/Ali-datasmith/SupplyChain-Risk-Engine-V2/actions/workflows/codeql-analysis.yml/badge.svg)
![Ruff](https://img.shields.io/badge/Ruff-compliant-brightgreen?style=flat-square)
![Mypy](https://img.shields.io/badge/Mypy-strict-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 1. Hero & Status Badges
> **Why this section exists:** Provides immediate technical credibility and automated proof of build health, test coverage, and strict type safety for senior data system architects and recruiters.

- **Python 3.12 / 3.13**: Built for modern Python runtimes.
- **CI Matrix**: Multi-version test verification via GitHub Actions.
- **CodeQL SAST**: Automated static analysis security scanning.
- **Zero-Error Ruff & Mypy**: Strict linting and typing compliance.

---

## 2. Executive Summary & V2 Architectural Highlights
> **Why this section exists:** Highlights performance paradigms and structural enhancements delivered in the V2 engine upgrade.

The **Supply Chain Risk Engine V2** is a high-throughput, B2B SaaS-grade command center engineered to ingest, validate, score, and visualize large-scale multi-tier supply chain data in real time.

### V2 Highlights & Paradigms:
1. **Zero-Copy Data Pipelines (Polars & DuckDB)**: High-speed vectorized lazy evaluations and zero-overhead out-of-core SQL cross-table joins.
2. **Strict Pandera Data Quality Gate**: Complete schema boundary protection preventing unvalidated or malformed supplier CSVs from reaching engine core.
3. **Resilient HTTP & GenAI Layer**: Integrated `httpx.Client` timeouts and `tenacity` exponential backoff retries mapped to taxonomy categories (`CAT_QUOTA`, `CAT_TIMEOUT`, `CAT_AUTH`, `CAT_SCHEMA`, `CAT_FALLBACK`).
4. **Argon2id Auth Gate & 1-Click Sandbox**: Enterprise password security combined with instant read-only recruiter demo access.
5. **Glassmorphic Obsidian Command Center UI**: Custom dark theme with neon cyan/indigo accents and non-laggy CSS backdrop blurs.

---

## 3. End-to-End System Architecture
> **Why this section exists:** Visualizes the raw data flow from multi-tier supplier CSV ingestion to executive C-suite briefings.

```text
┌───────────────────────────┐
│ Multi-Tier Supplier CSVs  │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐     ┌───────────────────────────┐
│   Pandera Ingestion Gate  │ ──▶ │ Out-of-Core DuckDB Joins  │
└─────────────┬─────────────┘     └─────────────┬─────────────┘
              │                                 │
              ▼                                 ▼
┌───────────────────────────┐     ┌───────────────────────────┐
│   Polars Vectorized Risk  │ ──▶ │ Live Threat Intel (RSS)  │
│      Scoring Engine       │     │ & Open-Meteo Weather API  │
└─────────────┬─────────────┘     └─────────────┬─────────────┘
              │                                 │
              ▼                                 ▼
┌───────────────────────────┐     ┌───────────────────────────┐
│ Structured GenAI Briefings│ ──▶ │ Board PDF & HTML Reports  │
│  (Google GenAI Pydantic)  │     │ & Interactive PyDeck Maps │
└───────────────────────────┘     └───────────────────────────┘
```

---

## 4. Mathematical Risk Scoring & Disruption Formulas
> **Why this section exists:** Explains the deterministic algorithmic foundation behind composite supplier threat calculations.

The engine computes a composite supplier risk index $R_c \in [0, 1]$ using weighted factor vectors:

$$R_c = \text{clamp}\left( w_b S_b + w_f S_f + w_o S_o + w_g S_g + w_a S_a, 0.0, 1.0 \right)$$

Where:
- **Base Risk ($S_b$)**: Standard normalized baseline risk score.
- **Financial Risk ($S_f$)**: Logarithmic scale of annual spend: $\frac{\ln(1 + \text{spend})}{\max(\ln(1 + \text{spend}))}$.
- **Operational Risk ($S_o$)**: Tier floor calculation: $1.0 - \frac{\text{tier} - 1}{3}$.
- **Geopolitical Exposure ($S_g$)**: Regional vulnerability coefficient (EMEA: 0.8, APAC: 0.7, LATAM: 0.6, NA: 0.3).
- **Audit Staleness ($S_a$)**: Half-life degradation ratio: $\min\left(1.0, \frac{\text{days since last audit}}{730}\right)$.

---

## 5. Directory Structure Tree
> **Why this section exists:** Provides repository scannability and highlights clean enterprise module separation.

```text
SupplyChain-Risk-Engine-V2/
├── .github/
│   └── workflows/
│       ├── ci.yml               # GitHub Actions CI matrix test runner
│       └── codeql-analysis.yml  # SAST security analysis workflow
├── ai/
│   ├── genai_client.py          # Google GenAI client factory
│   ├── narrative_generator.py   # Token-batched AI risk briefing generator
│   └── news_digest.py           # Typed news synthesis generator
├── engine/
│   ├── duckdb_joins.py          # Zero-copy DuckDB SQL queries
│   └── risk_scoring.py          # Vectorized Polars scoring algorithms
├── feeds/
│   ├── rss_client.py            # Non-blocking RSS news feed ingestion
│   └── weather_client.py        # Open-Meteo climate disruption client
├── geo/
│   └── map_builder.py           # GPU-accelerated PyDeck geospatial rendering
├── ingestion/
│   ├── csv_loader.py            # Optimized Polars CSV loader
│   └── validation_gate.py      # Pandera schema enforcement gate
├── reporting/
│   ├── html_report.py           # Jinja2 + Plotly interactive report builder
│   └── pdf_report.py            # Board-grade executive PDF engine
├── resilience/
│   └── http_client.py           # HTTPX client + Tenacity retry taxonomy
├── schemas/                     # Pydantic v2 & Pandera domain models
├── src/
│   ├── auth/                    # Argon2id security & session access gate
│   └── ui/                      # Glassmorphism dark styles & CSS injection
├── state/                       # Streamlit session state contract
├── telemetry/                   # Loguru structured logging handlers
├── tests/                       # Comprehensive pytest suite
├── app.py                       # Main Streamlit command center entrypoint
├── requirements.txt             # Production dependencies
└── README.md                    # System documentation
```

---

## 6. Local Setup & Execution Guide
> **Why this section exists:** Delivers bulletproof, step-by-step instructions for developers onboarding onto the repository.

```bash
# 1. Clone the repository
git clone https://github.com/Ali-datasmith/SupplyChain-Risk-Engine-V2.git
cd SupplyChain-Risk-Engine-V2

# 2. Create and activate virtual environment
python3.12 -m venv venv
source venv/bin/activate

# 3. Install production dependencies
pip install -r requirements.txt

# 4. Launch Streamlit Command Center
streamlit run app.py
```

---

## 7. Streamlit Cloud Deployment Guide
> **Why this section exists:** Demonstrates cloud readiness and zero-configuration Streamlit Community Cloud deployment.

1. Fork or push repository to GitHub.
2. Log in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **New app**, select your repository, branch (`main`), and main file path (`app.py`).
4. (Optional) In **Advanced Settings**, add secrets for `GEMINI_API_KEY` or `GEMINI_MODEL`.
5. Deploy! Dynamic `sys.path` resolution in `app.py` ensures seamless startup.

---

## 8. Testing & Quality Gates
> **Why this section exists:** Proves software reliability through strict test execution and static analysis tooling.

```bash
# Run complete test suite (79+ unit & integration tests)
python -m pytest -v

# Run linting with auto-fixing
ruff check . --fix

# Run strict static type checking
python -m mypy --explicit-package-bases app.py theme.py engine/ ingestion/ feeds/ geo/ reporting/ resilience/ schemas/ state/ telemetry/ ai/ src/
```

---

## 9. System Limitations & Production Roadmap
> **Why this section exists:** Demonstrates real-world architectural maturity and awareness of operational boundaries.

- **Current Limitations**: RSS feed availability relies on external provider endpoints; Gemini GenAI quota depends on API tier limits.
- **Production Roadmap**:
  - Integration with SAP/Oracle ERP webhooks.
  - Multi-tenant Role-Based Access Control (RBAC).
  - Streaming Kafka event pipeline ingestion.

---

## 10. License
> **Why this section exists:** Guarantees legal compliance for open-source enterprise usage.

Distributed under the MIT License. See `LICENSE` for details.
