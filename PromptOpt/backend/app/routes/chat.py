from fastapi import APIRouter, HTTPException, status, Depends
from app.models.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService
from typing import List
from app.services.evaluation_service import EvaluationService
from app.utils.guardrails import analyze_guardrails
from app.models.evaluation import GuardrailAnalysis
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Conversation, Message, Evaluation as ORMEval, Guardrail as ORMGuardrail, PromptVersion, User as ORMUser
from app.auth.security import get_current_user, require_admin

router = APIRouter()
llm_service = LLMService()
evaluation_service = EvaluationService()

# In-memory storage (deprecated; will remove after DB fully wired)
conversation_logs: List[dict] = []

@router.post("/chat", response_model=ChatResponse)
async def chat_with_hr_assistant(request: ChatRequest, db: Session = Depends(get_db), current_user: ORMUser = Depends(get_current_user)):
    """
    Chat with the HR assistant using LLM
    """
    try:
        # Generate response using LLM service
        response = await llm_service.generate_response(request)

        # Guardrails analysis and potential redaction/warn
        guardrails_report = analyze_guardrails(request.message, response.response)
        guardrails = GuardrailAnalysis(**guardrails_report)
        if guardrails.action == "redact" and guardrails.redacted_text:
            response.response = guardrails.redacted_text

        # Persist conversation and messages
        conv = Conversation(user_id=current_user.id)
        # Attach prompt version if selected
        if request.prompt_id:
            pv = db.query(PromptVersion).filter(PromptVersion.prompt_id == request.prompt_id, PromptVersion.is_active == True).order_by(PromptVersion.version.desc()).first()
            if pv:
                conv.prompt_version_id = pv.id
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

        # Legacy in-memory log
        conversation_logs.append({
            "user_id": current_user.id,
            "user_message": request.message,
            "assistant_response": response.response,
            "prompt_id": request.prompt_id,
            "response_time": response.response_time,
            "conversation_id": response.conversation_id,
            "guardrails_action": guardrails.action,
            "evaluation_overall": getattr(response.evaluation, "overall_score", None),
        })
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )

@router.get("/chat/logs", dependencies=[Depends(require_admin)])
def get_conversation_logs():
    return {"logs": conversation_logs}

@router.get("/chat/logs/{user_id}", dependencies=[Depends(require_admin)])
def get_user_conversation_logs(user_id: str):
    user_logs = [log for log in conversation_logs if log["user_id"] == user_id]
    return {"logs": user_logs}
