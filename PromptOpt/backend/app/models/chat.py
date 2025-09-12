from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.evaluation import EvaluationResult, GuardrailAnalysis


class ChatMessage(BaseModel):
	role: str  # 'user' or 'assistant'
	content: str
	timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
	message: str
	prompt_id: Optional[int] = None  # Which prompt template to use
	conversation_history: Optional[List[ChatMessage]] = []
	evaluate: Optional[bool] = False
	use_company_context: Optional[bool] = False


class ProvenanceItem(BaseModel):
	text: str
	score: Optional[float] = None
	source: Optional[str] = None


class ChatResponse(BaseModel):
	response: str
	prompt_used: Optional[str] = None
	response_time: Optional[float] = None
	conversation_id: Optional[str] = None
	evaluation: Optional[EvaluationResult] = None
	guardrails: Optional[GuardrailAnalysis] = None
	provenance: Optional[List[ProvenanceItem]] = None
	timestamp: Optional[datetime] = None
