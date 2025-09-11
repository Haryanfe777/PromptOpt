# Prompt Optimization Toolkit for HR Assistants

A practical prototype showing how to build an internal HR knowledge assistant with:
- Optimized prompt management with versioning and activation
- Guardrails (PII/profanity heuristics + optional OpenAI Moderation)
- Automated response evaluation (LLM judge + heuristics)
- Persistence, authentication (JWT), and admin UI

The goal: demonstrate real “LLM Ops” capabilities (prompt lifecycle, safety, evaluation) in a clean, runnable stack.

---

## What’s in the box
- `backend/` (FastAPI)
  - Auth (JWT), roles (admin/employee)
  - Chat API with evaluation and guardrails
  - Prompt CRUD with versioning and activation
  - DB via SQLAlchemy (SQLite dev), Alembic migrations
  - Optional moderation (OpenAI Moderation API)
  - Seed script for example users and prompts
- `frontend/` (React + webpack-dev-server)
  - Login, chat demo (toggle evaluation), role badge
  - Admin: Prompt Manager (create, version, activate, rename, delete) + Admin Logs

---

## Requirements
- Node.js 18+
- Python 3.10+
- An OpenAI API key

Optional (recommended):
- GitHub CLI installed
- Postgres for production use (prototype uses SQLite)

---

## Environment variables
Create `backend/.env` (or export vars in your shell). Example values:

```
OPENAI_API_KEY=sk-...
JWT_SECRET_KEY=change-this-in-prod
DATABASE_URL=sqlite:///./app.db
JUDGE_MODEL=gpt-4o-mini

# Moderation (optional)
ENABLE_MODERATION=false
MODERATION_MODE=block   # or redact
MODERATION_MODEL=omni-moderation-latest
```

There is also `backend/env.example` you can copy:
```
cp backend/env.example backend/.env
```

---

## Install & run (dev)
Open two terminals: one for backend, one for frontend.

### 1) Backend
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell (Windows)
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

# Apply database schema
alembic upgrade head

# Seed example users/prompts (admin/admin, employee/employee)
python -m app.utils.seed

# Run API
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Check health: http://127.0.0.1:8000/health

### 2) Frontend
```bash
cd frontend
npm install
npm start
```
Open http://localhost:8080

---

## How to demo (5 minutes)
1) Login
   - Use `admin/admin` (seeded). Role badge shows “Admin”.
2) Chat Demo
   - Ask an HR question, toggle “Evaluate response”.
   - You’ll see: assistant answer, guardrails, evaluation metrics.
3) Prompt Manager (Admin)
   - Create a prompt (title + content).
   - Select it → type new content → “Save as new version”.
   - “Activate” a version. Try the Chat Demo again.
   - Rename title or delete prompt when testing is done.
4) Admin Logs
   - View recent conversations (server enforces admin-only).

Optional:
- Turn on moderation (blocks or redacts flagged content): set `ENABLE_MODERATION=true` in backend env and restart.

---

## Architecture overview
- Frontend → FastAPI `/chat` → LLM (OpenAI) → response
- Guardrails
  - Heuristic checks: email/PII/profanity/injection → action: allow/warn/redact
  - Moderation (optional): OpenAI Moderation checks user input (block/redact)
- Evaluation
  - LLM judge (default `gpt-4o-mini`) returns scores (helpfulness, accuracy, …)
  - Heuristic fallback if judge call fails
- Persistence (SQLite dev)
  - Users, Prompts, PromptVersions, Conversations, Messages, Evaluations, Guardrails
- Auth
  - Login → JWT → role-based endpoints; UI gates on `/me`

---

## Key endpoints
- Auth
  - `POST /login` → `{ access_token }`
  - `GET /me` → `{ id, username, role }`
- Chat
  - `POST /chat` `{ message, prompt_id?, evaluate? }` → response + guardrails + evaluation
  - `GET /chat/logs` (admin) → recent summaries
- Prompts (admin for mutations)
  - `GET /prompts` → list prompts
  - `GET /prompts/{id}/versions` → all versions
  - `POST /prompts` → create (v1 active)
  - `PUT /prompts/{id}` → save as new version (deactivates previous)
  - `POST /prompts/{id}/activate/{version}` → activate version
  - `PATCH /prompts/{id}/title` → rename prompt
  - `DELETE /prompts/{id}` → delete prompt and versions

---

## Safety & evaluation
- Guardrails heuristic detects:
  - PII (emails, SSN/credit-card-like), profanity, prompt injection cues, sensitive topics
  - Actions: allow | warn | redact (and note)
- Moderation (optional): OpenAI Moderation checks incoming user text
  - `ENABLE_MODERATION=true`, choose `MODERATION_MODE=block|redact`
- Evaluation: LLM judge + fallback
  - Overall + criteria scores (helpfulness, accuracy, clarity, safety, relevance, tone)

---

## Tips & troubleshooting
- If `/chat` returns 401, sign in first and ensure the Authorization header is sent (frontend does this once logged in).
- If migrations drift, regenerate and apply:
  - `alembic revision --autogenerate -m "desc"`
  - `alembic upgrade head`
- To reset dev DB: stop backend, delete `backend/app.db`, re-run `alembic upgrade head` + `python -m app.utils.seed`.

---

## Roadmap (optional)
- A/B testing & analytics dashboards
- Cost tracking
- Postgres + Dockerized deploy
- Stronger auth (httpOnly cookies, CSRF)

---

## License
MIT (for learning/demo purposes).
