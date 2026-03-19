# 📈 CrewAI Financial Analyst

A production-grade agentic AI system that generates comprehensive stock investment reports. Submit a stock ticker and get an automated **BUY / SELL / HOLD** recommendation backed by real financial data and live news sentiment.

---

## 🏗️ Architecture

```
POST /api/v1/analyze  { "ticker": "TSLA" }
        │
        ▼
[Quant Agent] 🧮
    ├── FundamentalAnalysisTool → fetches P/E, EPS, Beta, Market Cap (yfinance)
    └── CompareStocksTool → benchmarks ticker vs S&P 500 (SPY)
        │
        │  (output passed as context)
        ▼
[Strategist Agent] 🧠
    ├── SentimentSearchTool → scrapes top 3 recent news articles (Firecrawl)
    └── Synthesizes numbers + news → BUY / SELL / HOLD verdict
        │
        ▼
Markdown Report (saved locally)
        │
        ├── 📦 Uploaded to Azure Blob Storage (permanent URL)
        └── 🗄️  Record saved to Azure PostgreSQL (queryable history)
```

---

## 📁 Project Structure

```
├── main.py                  # FastAPI entry point — wires routes and starts server
├── crew.py                  # Crew orchestrator — assembles agents, tasks, kicks off workflow
├── agents.py                # Agent definitions — Quant and Strategist personas + tools
├── tasks.py                 # Task definitions — work orders and prompt engineering
├── routes.py                # API route — POST /analyze endpoint controller
├── models.py                # Pydantic request/response schemas
├── config.py                # Settings management — loads and validates .env
├── database.py              # Azure PostgreSQL service — saves report records
├── storage.py               # Azure Blob Storage service — uploads markdown reports
└── investment_report_TSLA.md # Example generated report output
```

---

## ⚙️ How It Works

### 1. The Two Agents

**Quant Agent** — *"The Math Brain"*
- Role: Senior Quantitative Analyst
- Tools: `FundamentalAnalysisTool`, `CompareStocksTool`
- Focus: Hard financial metrics only — P/E, EPS, Beta, Market Cap
- `allow_delegation=False` — must use its own tools, cannot hand off to another agent

**Strategist Agent** — *"The Big Picture Brain"*
- Role: Chief Investment Strategist
- Tools: `SentimentSearchTool` (Firecrawl)
- Focus: News sentiment, leadership changes, regulatory issues
- Synthesizes Quant's numbers + news into a final verdict

### 2. Sequential Execution (Critical Design Decision)

```python
financial_crew = Crew(
    agents=[quant_agent, strategist_agent],
    tasks=tasks,
    process=Process.sequential,  # Quant MUST finish before Strategist starts
    memory=True,
    tracing=True
)
```

The Strategist's task uses `context=[quant_task]` to receive the Quant's output directly in its prompt. Without this, the Strategist would have no financial metrics to reason against.

### 3. Cloud Persistence

After the report is generated it is saved in two places for different purposes:

| Service | Purpose |
|---------|---------|
| **Azure Blob Storage** | Stores the full markdown report as a file with a permanent public URL — sent back to the user |
| **Azure PostgreSQL** | Stores a structured record (ticker, content, timestamp) — enables querying report history |

### 4. Settings Management

All secrets are loaded once at startup via `pydantic-settings` and cached with `@lru_cache()`:

```python
@lru_cache()
def get_settings() -> Settings:
    return Settings()  # .env file is read ONCE, then cached for all requests
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- OpenAI API key
- Firecrawl API key
- Azure subscription with:
  - Azure PostgreSQL
  - Azure Blob Storage
- LangSmith account (optional, for tracing)

### Installation

```bash
# Clone the repo
git clone <repo-url>
cd crewai-financial-analyst

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory:

```env
# AI Configuration
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL_NAME=gpt-4o

# Tool Configuration
FIRECRAWL_API_KEY=your_firecrawl_key

# Azure Infrastructure
AZURE_POSTGRES_CONNECTION_STRING=postgresql://user:password@host:5432/db?sslmode=require
AZURE_BLOB_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...

# Observability (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
```

> ⚠️ **Never hardcode credentials in code.** Always use the `.env` file and `config.py`.

---

## 🖥️ Usage

### Start the Server

```bash
uvicorn main:app --reload
```

### Analyze a Stock

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker": "TSLA"}'
```

### Example Response

```json
{
  "status": "success",
  "ticker": "TSLA",
  "report_content": "## Tesla (TSLA) Investment Report\n\n**Verdict: HOLD**\n...",
  "report_url": "https://youraccount.blob.core.windows.net/reports/investment_report_TSLA.md",
  "message": "Analysis complete and saved to cloud."
}
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/analyze` | Submit a ticker for full investment analysis |
| `GET`  | `/` | Health check |
| `GET`  | `/docs` | Interactive Swagger UI |

---

## 📊 Sample Report Output

The generated report includes:

- **Financial Metrics** — P/E ratio, EPS, Beta, Market Cap, 52-week high/low
- **Benchmark Comparison** — 1-year performance vs S&P 500
- **News Highlights** — Top 3 recent articles, analyst ratings, leadership changes
- **Risk Flags** — Legal liabilities, regulatory issues, strategic shifts
- **Final Verdict** — BUY / SELL / HOLD with full reasoning

See [`investment_report_TSLA.md`](./investment_report_TSLA.md) for a real example output.

---

## 🧰 Tech Stack

| Technology | Role |
|------------|------|
| **CrewAI** | Multi-agent orchestration framework |
| **OpenAI GPT-4o** | LLM powering both agents |
| **yfinance** | Real-time financial data (P/E, EPS, Beta) |
| **Firecrawl** | Web scraping for news and sentiment |
| **FastAPI** | REST API framework |
| **Pydantic** | Request/response validation + settings management |
| **Azure Blob Storage** | Persistent report file storage |
| **Azure PostgreSQL** | Structured report history database |
| **LangSmith** | Agent tracing and observability (optional) |

---

## 🔭 Observability

When `LANGCHAIN_TRACING_V2=true` is set, every agent step, tool call, and LLM interaction is traced in **LangSmith**. This lets you debug exactly what each agent did, what tools it called, and what the LLM reasoned at each step.