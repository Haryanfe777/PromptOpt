from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    password: str  # hashed in real use
    role: str  # 'admin' or 'employee'

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
