from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import Token
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User as ORMUser
from app.auth.security import verify_password, create_access_token

router = APIRouter()


def authenticate_user(db: Session, username: str, password: str) -> ORMUser | None:
	user = db.query(ORMUser).filter(ORMUser.username == username).first()
	if user and verify_password(password, user.password_hash):
		return user
	return None


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
	user = authenticate_user(db, form_data.username, form_data.password)
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
	token = create_access_token(subject=user.username, role=user.role)
	return {"access_token": token, "token_type": "bearer"}
