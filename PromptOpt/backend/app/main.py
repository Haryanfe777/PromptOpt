from fastapi import FastAPI
from app.routes import auth, prompt, chat
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine, SessionLocal
from app.db import models as orm
from app.auth.security import get_password_hash

app = FastAPI()

# CORS for development - adjust origins for production
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Seed default users
with SessionLocal() as db:
	if not db.query(orm.User).filter(orm.User.username == "admin").first():
		admin = orm.User(username="admin", password_hash=get_password_hash("admin"), role="admin")
		db.add(admin)
	if not db.query(orm.User).filter(orm.User.username == "employee").first():
		emp = orm.User(username="employee", password_hash=get_password_hash("employee"), role="employee")
		db.add(emp)
	db.commit()

app.include_router(auth.router)
app.include_router(prompt.router)
app.include_router(chat.router)

@app.get("/health")
def health_check():
	return {"status": "ok"}
