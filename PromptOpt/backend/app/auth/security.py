import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRES_MIN", "60"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
	return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return password_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
	to_encode = {"sub": subject, "role": role}
	expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
	to_encode.update({"exp": expire})
	return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> models.User:
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		username: str = payload.get("sub")
		if username is None:
			raise credentials_exception
		user = db.query(models.User).filter(models.User.username == username).first()
		if user is None:
			raise credentials_exception
		return user
	except JWTError:
		raise credentials_exception


def get_current_user_optional(db: Session = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme_optional)) -> Optional[models.User]:
	if not token:
		return None
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		username: str = payload.get("sub")
		if not username:
			return None
		return db.query(models.User).filter(models.User.username == username).first()
	except JWTError:
		return None


def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
	if current_user.role != "admin":
		raise HTTPException(status_code=403, detail="Admin privileges required")
	return current_user


def require_self_or_admin(target_user_id: int, current_user: models.User = Depends(get_current_user)) -> models.User:
	if current_user.role == "admin" or current_user.id == target_user_id:
		return current_user
	raise HTTPException(status_code=403, detail="Not authorized")
