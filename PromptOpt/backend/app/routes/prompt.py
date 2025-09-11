from fastapi import APIRouter, HTTPException, status, Depends
from app.models.prompt import Prompt as PromptSchema, PromptVersionOut
from typing import List
from app.models.evaluation import EvaluationRequest, EvaluationResult
from app.services.evaluation_service import EvaluationService
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Prompt as ORMPrompt, PromptVersion as ORMPromptVersion
from app.auth.security import require_admin, get_current_user

router = APIRouter()

eval_service = EvaluationService()

@router.get("/prompts", response_model=List[PromptSchema])
def list_prompts(db: Session = Depends(get_db)):
	rows = db.query(ORMPrompt).all()
	return [PromptSchema(id=r.id, title=r.title, content=(r.versions[0].content if r.versions else ""), created_by=r.created_by) for r in rows]

@router.get("/prompts/{prompt_id}/versions", response_model=List[PromptVersionOut])
def list_prompt_versions(prompt_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
	p = db.query(ORMPrompt).filter(ORMPrompt.id == prompt_id).first()
	if not p:
		raise HTTPException(status_code=404, detail="Prompt not found")
	versions = db.query(ORMPromptVersion).filter(ORMPromptVersion.prompt_id == prompt_id).order_by(ORMPromptVersion.version.desc()).all()
	return [PromptVersionOut(id=v.id, version=v.version, content=v.content, is_active=v.is_active, created_at=v.created_at) for v in versions]

@router.post("/prompts", response_model=PromptSchema)
def create_prompt(prompt: PromptSchema, db: Session = Depends(get_db), current_user=Depends(require_admin)):
	p = ORMPrompt(title=prompt.title, created_by=current_user.username)
	db.add(p)
	db.flush()
	v = ORMPromptVersion(prompt_id=p.id, version=1, content=prompt.content, is_active=True)
	db.add(v)
	db.commit()
	db.refresh(p)
	return PromptSchema(id=p.id, title=p.title, content=v.content, created_by=p.created_by)

@router.put("/prompts/{prompt_id}", response_model=PromptSchema)
def update_prompt(prompt_id: int, prompt: PromptSchema, db: Session = Depends(get_db), current_user=Depends(require_admin)):
	p = db.query(ORMPrompt).filter(ORMPrompt.id == prompt_id).first()
	if not p:
		raise HTTPException(status_code=404, detail="Prompt not found")
	latest_version = (db.query(ORMPromptVersion)
		.filter(ORMPromptVersion.prompt_id == prompt_id)
		.order_by(ORMPromptVersion.version.desc())
		.first())
	next_version = (latest_version.version + 1) if latest_version else 1
	v = ORMPromptVersion(prompt_id=prompt_id, version=next_version, content=prompt.content, is_active=True)
	if latest_version:
		latest_version.is_active = False
	db.add(v)
	db.commit()
	return PromptSchema(id=p.id, title=p.title, content=v.content, created_by=p.created_by)

@router.post("/prompts/{prompt_id}/activate/{version}")
def activate_prompt_version(prompt_id: int, version: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
	versions = db.query(ORMPromptVersion).filter(ORMPromptVersion.prompt_id == prompt_id).all()
	if not versions:
		raise HTTPException(status_code=404, detail="Prompt not found")
	found = None
	for v in versions:
		if v.version == version:
			found = v
			v.is_active = True
		else:
			v.is_active = False
	if not found:
		raise HTTPException(status_code=404, detail="Version not found")
	db.commit()
	return {"ok": True}

@router.delete("/prompts/{prompt_id}")
def delete_prompt(prompt_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
	p = db.query(ORMPrompt).filter(ORMPrompt.id == prompt_id).first()
	if not p:
		raise HTTPException(status_code=404, detail="Prompt not found")
	db.delete(p)
	db.commit()
	return {"ok": True}

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
