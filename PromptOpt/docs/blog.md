# Building a Practical HR Knowledge Assistant: From Idea to Running Prototype

This is a story about taking a vague idea — “let’s build a helpful HR assistant” — and turning it into a working prototype that anyone can run on a laptop. We focused on clarity, safety, and usefulness over buzzwords, and we wrote everything so a newcomer can follow along.

---

## The goal (in human words)
HR teams answer the same questions over and over: PTO, benefits, onboarding, policies, etc. We wanted a small internal tool that:
- Lets HR shape “how the assistant talks” using prompts
- Checks answers for safety (no PII, no prompt injection)
- Measures answer quality automatically
- Grounds answers in your company documents (not just generic internet knowledge)
- Is simple to run and easy to explain

We call it the Habeeb Prompt Optimization Toolkit.

---

## The plan (small steps, no magic)
1) Start with a clean backend (FastAPI) and a simple frontend (React)
2) Add core features one by one:
   - Auth (JWT) + roles (admin / employee)
   - Prompt management with versions and activation
   - Guardrails (heuristics + optional OpenAI moderation)
   - Evaluation (LLM judge + fallback heuristics)
   - RAG (Retrieval-Augmented Generation) for company-doc answers
   - Role-based prompt defaults and lightweight access rules
   - Logs and pruning (keep the last 10 conversations)
3) Make it easy to run (scripts + one-page README)

---

## What we built (at a glance)
- Backend: FastAPI, SQLAlchemy (SQLite in dev), Alembic migrations
- Frontend: React + webpack-dev-server
- LLM APIs: OpenAI Chat Completions + Embeddings
- RAG store: FAISS (local vector index) + small metadata file

---

## Architecture (plain English)
When you ask a question in the browser:
1) The frontend sends it to `/chat` with your token
2) The backend decides which system prompt to use (role default, or an explicit `prompt_id`)
3) If we’ve ingested company PDFs, we retrieve the most relevant snippets (RAG) and add them to the system prompt
4) We run guardrails and (optional) moderation on your question
5) The backend calls the LLM and returns:
   - The answer
   - Guardrails info
   - Evaluation scores (if requested)
   - Provenance (short snippets/sources used by RAG)
6) We store the conversation and keep only the most recent 10

---

## Why prompts matter (and versions!)
Prompts are like “role instructions.” Admins can:
- Create a prompt (title + content)
- Save a new version (without deleting history)
- Activate a version (becomes the default for that prompt)
- Rename or delete prompts

For quick demos we also support role-based defaults (env vars):
- `DEFAULT_PROMPT_ADMIN_ID`
- `DEFAULT_PROMPT_EMPLOYEE_ID`

If a `prompt_id` is not provided, we use those defaults.

---

## Guardrails (we play it safe)
We added two layers:
- Heuristic checks: PII-like patterns (emails/SSN), profanity, prompt-injection cues, sensitive topics → actions: allow / warn / redact
- Optional OpenAI Moderation: block or redact based on configuration

This is not “perfect security,” but it’s simple, visible, and easy to explain to non-engineers.

---

## Evaluation (is the answer any good?)
Click a checkbox to evaluate responses. We:
- Ask a judge model (default: `gpt-4o-mini`) to rate helpfulness, accuracy, clarity, safety, relevance, tone
- Fall back to a heuristic if the judge fails (so the UI never breaks)
- Return scores and a compact label

This encourages healthy, measurable iteration instead of guessing.

---

## RAG (answers from your company docs)
We wanted answers grounded in your policies—not generic internet knowledge. RAG flow:
1) Admin ingests PDFs via `/rag/ingest` (or a one-line Python command)
2) We chunk, embed, and index text with FAISS
3) At chat time, we retrieve top matches and append them to the system prompt
4) We show “Provenance” so users see which snippets informed the answer

No toggle required — if docs exist, we auto-use them.

---

## Lightweight role rules
We kept policies simple:
- Admin sees/uses everything
- Employees cannot use recruiting/onboarding prompts (guarded by title keywords)
- Prompts can still be selected explicitly with `prompt_id`, but defaults work out of the box

---

## Running it (two windows, that’s it)
Windows PowerShell:
```powershell
# Start backend + frontend
cd scripts
./dev.ps1 -OpenAIKey "YOUR_OPENAI_KEY"

# Optional smoke test (health, login, me, prompts, chat)
./smoke.ps1 -Base "http://127.0.0.1:8000" -User admin -Pass admin
```

macOS/Linux:
```bash
./scripts/dev.sh "$OPENAI_API_KEY"
./scripts/smoke.sh http://127.0.0.1:8000 admin admin
```

---

## Ingesting company PDFs (RAG)
Option A: Swagger UI (admin token required)
1) POST `/login` → copy `access_token`
2) Click “Authorize” in Swagger → `Bearer <token>`
3) POST `/rag/ingest` with your PDF file
4) GET `/rag/status` to verify `has_index: true`

Option B: One-liner from project folder (no HTTP)
```powershell
cd backend; .\.venv\Scripts\Activate.ps1
$env:OPENAI_API_KEY="sk-..."
python -c "from app.services.rag_service import RAGService; RAGService().ingest_pdf(r'backend\data\Employee_Handbook.pdf')"
```
(Use the bash variant on macOS/Linux.)

---

## What about costs and privacy?
- Dev uses SQLite + local FAISS index (no external DB)
- You control what gets ingested; provenance shows where content came from
- OpenAI calls happen only from your machine (via your API key)

---

## Trade-offs we embraced
- Simplicity over maximal features (no complex rules engine; role+keywords are enough for now)
- Local FAISS over managed vector DB (easy to reset, easy to demo)
- Lightweight guardrails instead of heavy policy frameworks (fast to explain)

---

## What’s next (when you’re ready)
- Add per-document management for RAG (list/delete/clear)
- Switch to Postgres for teams, add Docker for deployment
- UI polish: prompt categories, role-based filtering, richer diffs
- A/B testing and analytics dashboards

---

## Lessons learned
- A tiny amount of evaluation and provenance builds trust quickly
- “Boring” features (auth, CRUD, logs) matter to real users
- Write the README first; your future self will thank you

---

## Credits
- FastAPI, React, FAISS, OpenAI APIs
- Everyone who asked “but will HR actually use it?”

If you build on this, tell us what you shipped — we’d love to see it.
