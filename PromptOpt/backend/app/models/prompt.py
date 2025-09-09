from pydantic import BaseModel
from typing import Optional

class Prompt(BaseModel):
    id: Optional[int] = None
    title: str
    content: str
    created_by: str
