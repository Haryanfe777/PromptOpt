from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import User, UserLogin, Token
from typing import Dict

router = APIRouter()

fake_users_db: Dict[str, User] = {
    "admin": User(username="admin", password="admin", role="admin"),
    "employee": User(username="employee", password="employee", role="employee"),
}

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if user and user.password == password:
        return user
    return None

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    # For MVP, return a fake token
    return {"access_token": f"fake-token-for-{user.username}", "token_type": "bearer"}
