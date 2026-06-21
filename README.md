# Backtesting Framework for Equity-Based Strategies

An end-to-end backtesting platform for fundamental, equity-based strategies
on the Indian (NSE) market: configurable filters, single/composite ranking,
equal/market-cap/metric-weighted position sizing, periodic rebalancing with
compounding, and full performance analytics vs. the Nifty 50 benchmark —
with a Next.js terminal-style UI to configure, run, and analyse it all.

**Tech stack:** FastAPI (Python) · SQLAlchemy · PostgreSQL (Supabase) ·
Next.js (TypeScript) + Tailwind CSS · Yahoo Finance (`yfinance`) for data.

## Repository Structure

```
.
├── backend/              FastAPI service (see backend/README.md for full docs)
│   └── app/
│       ├── core/           config, logging
│       ├── db/              SQLAlchemy session/base
│       ├── models/          ORM models = DB schema
│       ├── schemas/         Pydantic request/response contracts
│       ├── data_collection/  Yahoo Finance ingestion pipeline
│       ├── backtest_engine/  Filters, ranking, sizing, rebalancing, metrics
│       ├── strategies/       Prebuilt strategy configs (bonus)
│       └── api/routes/       HTTP layer
├── frontend/              Next.js + Tailwind UI (see frontend/README.md for full docs)
│   ├── app/                 Routes: New Backtest, Run History, Results,
│   │                          Prebuilt Strategies, Compare Runs
│   ├── components/          backtest-form/, results/, runs/, strategies/,
│   │                          compare/, layout/, ui/ (all modular, no
│   │                          single mega-component)
│   ├── hooks/                One React Query hook per backend endpoint
│   └── lib/                  Typed API client, types, formatting helpers
├── docker-compose.yml     Local Postgres for development
└── README.md              This file
```

## Quick Start

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # set DATABASE_URL (Supabase or local Postgres)
python -m app.data_collection.pipeline   # ingest ~125 NSE companies + Nifty 50
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

Full architecture, schema rationale, API reference, and documented
assumptions: **[backend/README.md](backend/README.md)**.

### Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```
App: http://localhost:3000

Full architecture, design-system rationale, and requirement-to-component
mapping: **[frontend/README.md](frontend/README.md)**.
