import os
from typing import Optional
import openai
from app.models.evaluation import EvaluationResult, EvalCriteriaScores

JUDGE_SYSTEM_PROMPT = (
	"You are an expert HR quality evaluator. Score the assistant response from 0-5 on: "
	"helpfulness, accuracy, clarity, safety, relevance, and tone. "
	"Return strict JSON with keys: helpfulness, accuracy, clarity, safety, relevance, tone, overall, label, comments, hallucination_risk."
)


class EvaluationService:
	def __init__(self):
		self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"))
		self.judge_model = os.getenv("JUDGE_MODEL", "gpt-4o-mini")

	async def evaluate(self, user_message: str, assistant_response: str, prompt_used: Optional[str] = None) -> EvaluationResult:
		try:
			messages = [
				{"role": "system", "content": JUDGE_SYSTEM_PROMPT},
				{"role": "user", "content": (
					f"Prompt (system):\n{prompt_used or '[none]'}\n\n"
					f"User: {user_message}\n\nAssistant: {assistant_response}\n\n"
					"Please return JSON only."
				)},
			]

			resp = self.client.chat.completions.create(
				model=self.judge_model,
				messages=messages,
				temperature=0.0,
				max_tokens=300,
			)
			content = resp.choices[0].message.content
			data = self._safe_parse_json(content)
			if not data:
				return self._heuristic_fallback(assistant_response)

			criteria = EvalCriteriaScores(
				helpfulness=float(data.get("helpfulness", 3)),
				accuracy=float(data.get("accuracy", 3)),
				clarity=float(data.get("clarity", 3)),
				safety=float(data.get("safety", 3)),
				relevance=float(data.get("relevance", 3)),
				tone=float(data.get("tone", 3)),
			)
			overall = float(data.get("overall", sum([criteria.helpfulness, criteria.accuracy, criteria.clarity, criteria.safety, criteria.relevance, criteria.tone]) / 6))
			return EvaluationResult(
				overall_score=overall,
				criteria=criteria,
				label=str(data.get("label", "unknown")),
				comments=str(data.get("comments", "")),
				hallucination_risk=str(data.get("hallucination_risk", "unknown")),
				judge_model=self.judge_model,
			)
		except Exception:
			return self._heuristic_fallback(assistant_response)

	def _heuristic_fallback(self, assistant_response: str) -> EvaluationResult:
		length = len(assistant_response.strip())
		helpfulness = 2.0 + min(3.0, length / 500)
		clarity = 2.5
		accuracy = 2.5
		safety = 3.0
		relevance = 2.5
		one = 3.0
		criteria = EvalCriteriaScores(
			helpfulness=helpfulness,
			accuracy=accuracy,
			clarity=clarity,
			safety=safety,
			relevance=relevance,
			tone=one,
		)
		overall = sum([helpfulness, accuracy, clarity, safety, relevance, one]) / 6
		label = "good" if overall >= 4 else ("average" if overall >= 3 else "poor")
		return EvaluationResult(
			overall_score=overall,
			criteria=criteria,
			label=label,
			comments="Heuristic fallback used",
			hallucination_risk="unknown",
			judge_model="heuristic",
		)

	def _safe_parse_json(self, text: str):
		import json
		try:
			start = text.find('{')
			end = text.rfind('}')
			if start == -1 or end == -1:
				return None
			return json.loads(text[start:end+1])
		except Exception:
			return None
