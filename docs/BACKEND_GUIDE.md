

# GFPS – Backend Guide

The backend is a FastAPI-based service that exposes:

- API endpoints (auth, fixtures, coupons, favorites, alerts, chat, stats)
- Background alert engine
- Prediction engine

---

## 1. Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env values
uvicorn main:app --reload
