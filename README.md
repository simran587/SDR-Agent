# Grok-Powered SDR Demo

## Overview
A lean SDR tool using Grok API for lead qual and outreach. Demo-ready in 4hrs!

## Setup
1. Redeem promo at [console.x.ai](https://console.x.ai) → Add key to `grok_client.py`.
2. `pip install -r requirements.txt` or `docker-compose up`.
3. Run `streamlit run app.py`.
4. Set MOCK=False in `grok_client.py` for live Grok.

## Features
- **Qualification**: Grok scores leads via BANT + user ICP.
- **Messaging**: Personalized emails.
- **DB**: SQLite CRUD, search, logging.
- **Eval**: `pytest evals.py` for prompt tuning.

## Technical Specs
- Prompts: CoT-optimized for sales accuracy.
- Error Handling: JSON fallback, logging TBD.
- Scalability: Add Redis for prod caching.

## Troubleshooting
- API Errors: Check key/quotas at console.x.ai.
- DB Issues: Delete `leads.db`, re-init.
- Evals Fail: Tweak temp=0.5 for consistency.

## Iteration Recs
From evals: Add multi-turn for deeper qual. Expand stages: Use Grok for auto-progression.