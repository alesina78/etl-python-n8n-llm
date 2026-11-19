# 💱 FX Medallion ETL Pipeline with Python, n8n & Local LLM (Ollama)

**Automated Currency Exchange Data Engineering Pipeline orchestrated with Python, n8n & Local LLMs**

*End-to-end Medallion Architecture (Bronze → Silver → Gold) transforming raw financial APIs into AI-powered market insights — configured to run locally and free with Ollama*

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-000000?style=flat-square&logo=ollama&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-Workflow_Automation-EA4B71?style=flat-square&logo=n8n&logoColor=white)

---

## 🎯 Overview

Financial and operational teams often struggle to monitor daily foreign exchange (FX) fluctuations and translate raw exchange rate numbers into actionable context.

This repository implements a **Medallion ETL pipeline** that automates the ingestion of currency rates via the **Frankfurter API**, enforces idempotent relational modeling in **SQLite** (`data/demo.sqlite`), and uses a **local LLM via Ollama** (`llama3` by default) to generate automated executive summaries and market variation insights on the Gold layer — without requiring paid API credits.

Orchestrated via **CLI** or **n8n workflows**, the pipeline demonstrates data engineering fundamentals: idempotent `UPSERT` operations, clear separation of concerns across storage layers (`fx_bronze`, `fx_silver`, `fx_gold`), and local LLM enrichment.

> *"Combining classic idempotent data engineering patterns with local generative AI enrichment."*

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
         │  (Window Comparison D vs D-1 & Local LLM Enrichment)
         ▼
┌──────────────────────┐
│     GOLD LAYER       │  ──► fx_gold: Daily % variance + local LLM executive analysis & notes
└──────────────────────┘
```

### Layer Breakdown

| Layer | Table | Module | Responsibility & Engineering Features |
|:--|:--|:--|:--|
| **🥉 Bronze** | `fx_bronze` | `fx_extract.py`<br>`fx_bronze_loader.py` | Stores raw JSON payloads (`raw_json`), base currency, reference dates, and ingestion timestamps for auditability and replayability. |
| **🥈 Silver** | `fx_silver` | `fx_silver_transform.py` | Normalizes currency rates into relational rows (`ref_date`, `base`, `symbol`, `rate`) with unique index support for idempotency. |
| **🥇 Gold** | `fx_gold` | `fx_gold_enrich.py` | Computes comparisons against previous dates and calls the local **Ollama** endpoint (`http://localhost:11434/v1`) to generate `analysis` and `ia_notes`. |

---

## 📂 Repository Structure

```text
etl-python-n8n-llm/
├── data/
│   └── demo.sqlite              # Local SQLite database (ignored in Git or kept as demo if desired)
├── src/
│   ├── config.py                # Environment variables & Ollama / SQLite configuration loader
│   ├── fx_db.py                 # SQLAlchemy engine factory & DDL schema bootstrapper
│   ├── fx_extract.py            # HTTP client for Frankfurter FX API
│   ├── fx_bronze_loader.py      # Raw payload persistence into Bronze layer
│   ├── fx_silver_transform.py   # JSON flattening & idempotent UPSERT into Silver layer
│   ├── fx_gold_enrich.py        # Delta calculation & local LLM enrichment for Gold layer
│   ├── fx_pipeline.py           # Main CLI orchestrator (--run bronze silver gold)
│   └── fx_queries_demo.py       # Pandas diagnostic script to inspect Silver & Gold tables
├── .env.example                 # Example environment variables template
├── .gitignore                   # Security rules protecting credentials, local DB & venv
└── README.md                    # Project documentation
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/alesina78/etl-python-n8n-llm.git
cd etl-python-n8n-llm
```

### 2. Install Ollama & pull a local model

Install [Ollama](https://ollama.com/) on your machine, ensure the service is running locally on port `11434`, and download the model:

```bash
ollama pull llama3
```

### 3. Set up the virtual environment & dependencies

```bash
python -m venv venv
venv\Scripts\activate            # Windows (CMD)
# source venv/Scripts/activate  # Windows (Git Bash)
# source venv/bin/activate      # Linux / macOS

pip install requests sqlalchemy pandas openai python-dotenv
```

### 4. Configure Environment Variables

Create a `.env` file in the **root directory** of the project (never commit `.env` with sensitive data):

```env
DB_DSN=sqlite:///data/demo.sqlite
OPENAI_API_KEY=ollama
OPENAI_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434/v1
```

### 5. Run the ETL Pipeline

Execute the full Medallion flow (`bronze` → `silver` → `gold`):

```bash
python -m src.fx_pipeline --base USD --symbols BRL EUR GBP JPY CAD CHF AUD ARS --run bronze silver gold
```

### 6. Inspect Results

Run the diagnostic script to inspect the persisted tables in the terminal:

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