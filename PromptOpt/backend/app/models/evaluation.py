from pydantic import BaseModel, Field
from typing import Optional


class EvalCriteriaScores(BaseModel):
	helpfulness: float = Field(ge=0.0, le=5.0, description="How helpful is the response?")
	accuracy: float = Field(ge=0.0, le=5.0, description="How factually accurate is the response?")
	clarity: float = Field(ge=0.0, le=5.0, description="How clear and well-structured is the response?")
	safety: float = Field(ge=0.0, le=5.0, description="Does the response avoid unsafe content?")
	relevance: float = Field(ge=0.0, le=5.0, description="How relevant is the response to the user's request?")
	tone: float = Field(ge=0.0, le=5.0, description="Is the tone appropriate for HR?")


class EvaluationResult(BaseModel):
	overall_score: float = Field(ge=0.0, le=5.0)
	criteria: EvalCriteriaScores
	label: Optional[str] = Field(default=None, description="Overall label like 'good', 'average', 'poor'")
	comments: Optional[str] = None
	hallucination_risk: Optional[str] = Field(default=None, description="low | medium | high")
	judge_model: Optional[str] = None


class GuardrailAnalysis(BaseModel):
	contains_pii: bool = False
	contains_profanity: bool = False
	prompt_injection_suspected: bool = False
	contains_sensitive_topics: bool = False
	redacted_text: Optional[str] = None
	action: str = Field(default="allow", description="allow | warn | block | redact")
	message: Optional[str] = None


class EvaluationRequest(BaseModel):
	prompt_used: Optional[str] = None
	user_message: str
	assistant_response: str
