from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Prompt(BaseModel):
    id: Optional[int] = None
    title: str
    content: str
    created_by: str

class PromptVersionOut(BaseModel):
    id: int
    version: int
    content: str
    is_active: bool
    created_at: Optional[datetime] = None
