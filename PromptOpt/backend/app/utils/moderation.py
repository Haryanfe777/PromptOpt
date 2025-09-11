import os
from typing import Literal, Tuple
import openai

ModerationAction = Literal['allow', 'block', 'redact']

class ModerationService:
	def __init__(self):
		self.enabled = os.getenv('ENABLE_MODERATION', 'false').lower() == 'true'
		self.mode: ModerationAction = os.getenv('MODERATION_MODE', 'block')  # block|redact
		self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY', 'your-api-key-here'))
		self.model = os.getenv('MODERATION_MODEL', 'omni-moderation-latest')

	def check(self, text: str) -> Tuple[ModerationAction, str | None]:
		if not self.enabled:
			return 'allow', None
		try:
			res = self.client.moderations.create(model=self.model, input=text)
			flagged = bool(res.results[0].flagged)
			if flagged:
				if self.mode == 'redact':
					return 'redact', '[REDACTED FOR SAFETY]'
				return 'block', None
			return 'allow', None
		except Exception:
			# Fail open for demo; in prod consider fail-closed
			return 'allow', None
