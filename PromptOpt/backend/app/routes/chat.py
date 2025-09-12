from fastapi import APIRouter, HTTPException, status, Depends
from app.models.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService
from typing import List
from app.services.evaluation_service import EvaluationService
from app.utils.guardrails import analyze_guardrails
from app.utils.moderation import ModerationService
from app.models.evaluation import GuardrailAnalysis
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.database import get_db
from app.db.models import Conversation, Message, Evaluation as ORMEval, Guardrail as ORMGuardrail, PromptVersion, User as ORMUser
from app.auth.security import get_current_user, require_admin
from app.services.rag_service import RAGService

router = APIRouter()
llm_service = LLMService()
evaluation_service = EvaluationService()
moderation = ModerationService()
rag_service = RAGService()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_hr_assistant(request: ChatRequest, db: Session = Depends(get_db), current_user: ORMUser = Depends(get_current_user)):
    """
    Chat with the HR assistant using LLM
    """
    try:
        # Pre-check moderation on user input
        action, replacement = moderation.check(request.message)
        if action == 'block':
            raise HTTPException(status_code=400, detail="Message blocked by moderation policy")
        if action == 'redact' and replacement:
            request.message = replacement

        # Resolve system prompt from DB if prompt_id specified
        system_prompt_override = None
        active_pv = None
        if request.prompt_id:
            active_pv = (
                db.query(PromptVersion)
                .filter(PromptVersion.prompt_id == request.prompt_id, PromptVersion.is_active == True)
                .order_by(PromptVersion.version.desc())
                .first()
            )
            if active_pv:
                system_prompt_override = active_pv.content

        # RAG: add company context to the system prompt if requested
        if request.use_company_context:
            base = system_prompt_override or llm_service.get_prompt_content(request.prompt_id)
            system_prompt_override = rag_service.build_system_prompt(base_prompt=base, query=request.message, top_k=4)

        # Generate response using LLM service (DB prompt wins)
        response = await llm_service.generate_response(request, system_prompt_override=system_prompt_override)

        # Guardrails analysis and potential redaction/warn
        guardrails_report = analyze_guardrails(request.message, response.response)
        guardrails = GuardrailAnalysis(**guardrails_report)
        if guardrails.action == "redact" and guardrails.redacted_text:
            response.response = guardrails.redacted_text

        # Persist conversation and messages
        conv = Conversation(user_id=current_user.id)
        if active_pv:
            conv.prompt_version_id = active_pv.id
        db.add(conv)
        db.flush()

        m_user = Message(conversation_id=conv.id, role="user", content=request.message)
        m_assistant = Message(conversation_id=conv.id, role="assistant", content=response.response)
        db.add_all([m_user, m_assistant])
        db.flush()

        # Optional evaluation
        if request.evaluate:
            evaluation = await evaluation_service.evaluate(
                user_message=request.message,
                assistant_response=response.response,
                prompt_used=response.prompt_used,
            )
            response.evaluation = evaluation
            db.add(ORMEval(
                conversation_id=conv.id,
                message_id=m_assistant.id,
                overall=evaluation.overall_score,
                criteria=evaluation.criteria.dict(),
                label=evaluation.label,
                judge_model=evaluation.judge_model,
            ))

        # Attach guardrails info
        response.guardrails = guardrails
        db.add(ORMGuardrail(
            conversation_id=conv.id,
            message_id=m_assistant.id,
            action=guardrails.action,
            report=guardrails.dict(),
        ))

        db.commit()
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )

@router.get("/chat/logs", dependencies=[Depends(require_admin)])
def get_conversation_logs(db: Session = Depends(get_db)):
    items = (
        db.query(Conversation)
        .order_by(desc(Conversation.started_at))
        .limit(50)
        .all()
    )
    out = []
    for c in items:
        out.append({
            "id": c.id,
            "user_id": c.user_id,
            "prompt_version_id": c.prompt_version_id,
            "started_at": c.started_at.isoformat(),
            "message_count": len(c.messages),
        })
    return {"logs": out}

@router.get("/chat/logs/user/{user_id}", dependencies=[Depends(require_admin)])
def get_user_conversation_logs(user_id: int, db: Session = Depends(get_db)):
    items = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(desc(Conversation.started_at))
        .all()
    )
    out = []
    for c in items:
        out.append({
            "id": c.id,
            "user_id": c.user_id,
            "prompt_version_id": c.prompt_version_id,
            "started_at": c.started_at.isoformat(),
            "message_count": len(c.messages),
        })
    return {"logs": out}
