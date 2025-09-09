from fastapi import APIRouter, HTTPException, status, Depends
from app.models.prompt import Prompt
from typing import List
from app.models.evaluation import EvaluationRequest, EvaluationResult
from app.services.evaluation_service import EvaluationService

router = APIRouter()

# In-memory DB for MVP
prompts_db: List[Prompt] = []

eval_service = EvaluationService()

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

@router.post("/evaluate", response_model=EvaluationResult)
async def evaluate_response(payload: EvaluationRequest):
    try:
        result = await eval_service.evaluate(
            user_message=payload.user_message,
            assistant_response=payload.assistant_response,
            prompt_used=payload.prompt_used,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
