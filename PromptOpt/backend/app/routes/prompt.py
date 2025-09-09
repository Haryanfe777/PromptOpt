from fastapi import APIRouter, HTTPException, status, Depends
from app.models.prompt import Prompt
from typing import List

router = APIRouter()

# In-memory DB for MVP
prompts_db: List[Prompt] = []

@router.get("/prompts", response_model=List[Prompt])
def list_prompts():
    return prompts_db

@router.post("/prompts", response_model=Prompt)
def create_prompt(prompt: Prompt):
    prompt.id = len(prompts_db) + 1
    prompts_db.append(prompt)
    return prompt

@router.put("/prompts/{prompt_id}", response_model=Prompt)
def update_prompt(prompt_id: int, prompt: Prompt):
    for idx, p in enumerate(prompts_db):
        if p.id == prompt_id:
            prompts_db[idx] = prompt
            return prompt
    raise HTTPException(status_code=404, detail="Prompt not found")

@router.delete("/prompts/{prompt_id}")
def delete_prompt(prompt_id: int):
    for idx, p in enumerate(prompts_db):
        if p.id == prompt_id:
            prompts_db.pop(idx)
            return {"ok": True}
    raise HTTPException(status_code=404, detail="Prompt not found")
