from fastapi import FastAPI
from app.routes import auth, prompt, chat
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# CORS for development - adjust origins for production
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Note: Database tables and seed data are managed via Alembic migrations.
# To bootstrap a fresh dev DB with seed users, set BOOTSTRAP_DEV=true and run a one-time script.

app.include_router(auth.router)
app.include_router(prompt.router)
app.include_router(chat.router)

@app.get("/health")
def health_check():
	return {"status": "ok"}
