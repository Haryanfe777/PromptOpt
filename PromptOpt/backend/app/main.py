from fastapi import FastAPI
from app.routes import auth, prompt, chat
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# CORS for development - adjust origins for production
app.add_middleware(
	CORSMiddleware,
	allow_origins=[
		"http://localhost:8080",
		"http://127.0.0.1:8080",
	],
	allow_credentials=True,
	allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
	allow_headers=["*"],
)

# Note: Database tables and seed data are managed via Alembic migrations.
# To bootstrap a fresh dev DB with seed users, set BOOTSTRAP_DEV=true and run a one-time script.

from app.routes import rag  # register after app is created
app.include_router(auth.router)
app.include_router(prompt.router)
app.include_router(chat.router)
app.include_router(rag.router)

@app.get("/health")
def health_check():
	return {"status": "ok"}
