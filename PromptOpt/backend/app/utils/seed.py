from app.db.database import SessionLocal
from app.db import models as orm
from app.auth.security import get_password_hash

EXAMPLE_PROMPTS = [
	{"title": "Recruiting Assistant", "content": "You are an HR assistant for recruiting..."},
	{"title": "Onboarding Assistant", "content": "You help new hires with onboarding..."},
	{"title": "HR FAQ", "content": "You answer general HR policy questions..."},
]

def seed():
	with SessionLocal() as db:
		if not db.query(orm.User).filter(orm.User.username == "admin").first():
			admin = orm.User(username="admin", password_hash=get_password_hash("admin"), role="admin")
			db.add(admin)
		if not db.query(orm.User).filter(orm.User.username == "employee").first():
			emp = orm.User(username="employee", password_hash=get_password_hash("employee"), role="employee")
			db.add(emp)
		db.commit()

		for p in EXAMPLE_PROMPTS:
			existing = db.query(orm.Prompt).filter(orm.Prompt.title == p["title"]).first()
			if existing:
				continue
			prompt = orm.Prompt(title=p["title"], created_by="admin")
			db.add(prompt)
			db.flush()
			version = orm.PromptVersion(prompt_id=prompt.id, version=1, content=p["content"], is_active=True)
			db.add(version)
			db.commit()

if __name__ == "__main__":
	seed()
