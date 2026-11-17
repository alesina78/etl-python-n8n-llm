# 💱 FX Medallion ETL Pipeline with Python, n8n & LLM

**Automated Currency Exchange Data Engineering Pipeline orchestrated with Python, n8n & OpenAI LLMs**

*End-to-end Medallion Architecture (Bronze → Silver → Gold) transforming raw financial APIs into AI-powered market insights*

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=flat-square&logo=openai&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-Workflow_Automation-EA4B71?style=flat-square&logo=n8n&logoColor=white)

---

## 🎯 Overview

Financial and operational teams often struggle to monitor daily foreign exchange (FX) fluctuations and translate raw exchange rate numbers into actionable context.

This repository implements a **production-ready Medallion ETL pipeline** that automates the ingestion of real-time and historical currency rates via the **Frankfurter API**, enforces idempotent relational modeling in **SQLite/PostgreSQL**, and leverages **OpenAI LLMs (`gpt-4o-mini`)** to generate automated executive summaries and market variation insights on the Gold layer.

Orchestrated via **CLI** or **n8n workflows**, the pipeline demonstrates solid data engineering fundamentals: idempotent `UPSERT` operations, clear separation of concerns across storage layers, and structured AI enrichment with deterministic fallback handling.

> *"Combining classic idempotent data engineering patterns with generative AI enrichment."*

---

## 🏗️ Architecture & Data Flow

```text
[Frankfurter REST API]
         │
         ▼  (Extract & Raw Load)
┌──────────────────────┐
│    BRONZE LAYER      │  ──► fx_bronze: Immutable raw JSON payloads + ingestion metadata
└────────┬─────────────┘
         │  (Parse, Type-Cast & Idempotent UPSERT)
         ▼
┌──────────────────────┐
│    SILVER LAYER      │  ──► fx_silver: Normalized tabular currency pairs (ref_date, base, symbol, rate)
└────────┬─────────────┘
         │  (Window Comparison D vs D-1 & LLM Enrichment)
         ▼
┌──────────────────────┐
│     GOLD LAYER       │  ──► fx_gold: Daily % variance + AI-generated executive analysis & notes
└──────────────────────┘
```

### Layer Breakdown

| Layer | Table | Module | Responsibility & Engineering Features |
|:--|:--|:--|:--|
| **🥉 Bronze** | `fx_bronze` | `fx_extract.py`<br>`fx_bronze_loader.py` | Stores full JSON responses (`raw_json`), base currency, reference dates, and ingestion timestamps for full auditability and replayability. |
| **🥈 Silver** | `fx_silver` | `fx_silver_transform.py` | Explodes nested JSON rates into clean relational rows; implements `ON CONFLICT DO UPDATE` (UPSERT) to guarantee idempotency. |
| **🥇 Gold** | `fx_gold` | `fx_gold_enrich.py` | Computes day-over-day percentage deltas (`pct_change`) and invokes **GPT-4o-mini** to produce structured financial commentary (`short_text`, `analysis`, `ia_notes`). |

---

## 📂 Repository Structure

```text
etl-python-n8n-llm/
├── src/
│   ├── config.py                # Environment variables & database DSN configuration loader
│   ├── fx_db.py                 # SQLAlchemy engine factory & DDL schema bootstrapper
│   ├── fx_extract.py            # HTTP client for Frankfurter FX API (latest & historical)
│   ├── fx_bronze_loader.py      # Raw payload persistence into Bronze layer
│   ├── fx_silver_transform.py   # JSON flattening & idempotent UPSERT into Silver layer
│   ├── fx_gold_enrich.py        # Delta calculation & OpenAI LLM enrichment for Gold layer
│   ├── fx_pipeline.py           # Main CLI orchestrator (--mode full | extract | transform | enrich)
│   └── fx_queries_demo.py       # Pandas diagnostic script to inspect Silver & Gold tables
├── .gitignore                   # Security rules protecting credentials, local SQLite DB & venv
└── README.md                    # Project documentation
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/alesina78/etl-python-n8n-llm.git
cd etl-python-n8n-llm
```

### 2. Set up the virtual environment & dependencies

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
# source venv/Scripts/activate  # Windows (Git Bash)

pip install requests sqlalchemy pandas openai python-dotenv
```

### 3. Configure Environment Variables

Create a `.env` file inside `src/` (or in the root directory — never commit this file):

```env
DB_DSN=sqlite:///data/demo.sqlite
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

### 4. Run the ETL Pipeline

**Execute full end-to-end Medallion flow (`extract` → `transform` → `enrich`):**

```bash
python -m src.fx_pipeline --mode full --base USD --symbols BRL,EUR,GBP
```

**Execute individual stages:**

```bash
# Ingestion only (Bronze)
python -m src.fx_pipeline --mode extract --base USD --symbols BRL,EUR

# Transformation only (Silver)
python -m src.fx_pipeline --mode transform

# AI Enrichment only (Gold)
python -m src.fx_pipeline --mode enrich
```

### 5. Inspect Results

Run the diagnostic utility to display formatted Silver and Gold tables directly in your terminal:

```bash
python -m src.fx_queries_demo
```

---

## 👤 Author

**Alessandro Lesina Giordano**  
*Senior Data Engineer & Analytics Specialist*  
*Bridging 25+ years of enterprise data architecture with modern Data Engineering, Analytics and AI*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-alessandrolesina-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/alessandrolesina/)
[![GitHub](https://img.shields.io/badge/GitHub-alesina78-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/alesina78)
[![Email](https://img.shields.io/badge/Email-giordano.dba@gmail.com-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:giordano.dba@gmail.com)
