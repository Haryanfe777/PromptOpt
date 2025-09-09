from fastapi import APIRouter, HTTPException, status
from app.models.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService
from typing import List
from app.services.evaluation_service import EvaluationService
from app.utils.guardrails import analyze_guardrails
from app.models.evaluation import GuardrailAnalysis

router = APIRouter()
llm_service = LLMService()
evaluation_service = EvaluationService()

# In-memory storage for conversation logs (MVP)
conversation_logs: List[dict] = []

@router.post("/chat", response_model=ChatResponse)
async def chat_with_hr_assistant(request: ChatRequest):
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

        # Optional evaluation
        if request.evaluate:
            evaluation = await evaluation_service.evaluate(
                user_message=request.message,
                assistant_response=response.response,
                prompt_used=response.prompt_used,
            )
            response.evaluation = evaluation

        # Attach guardrails info
        response.guardrails = guardrails
        
        # Log the conversation
        log_entry = {
            "user_id": request.user_id,
            "user_message": request.message,
            "assistant_response": response.response,
            "prompt_id": request.prompt_id,
            "response_time": response.response_time,
            "conversation_id": response.conversation_id,
            "guardrails_action": guardrails.action,
            "evaluation_overall": getattr(response.evaluation, "overall_score", None),
        }
        conversation_logs.append(log_entry)
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )

@router.get("/chat/logs")
def get_conversation_logs():
    """
    Get all conversation logs (admin only in production)
    """
    return {"logs": conversation_logs}

@router.get("/chat/logs/{user_id}")
def get_user_conversation_logs(user_id: str):
    """
    Get conversation logs for a specific user
    """
    user_logs = [log for log in conversation_logs if log["user_id"] == user_id]
    return {"logs": user_logs}
