import re
from typing import Tuple

PII_PATTERNS = [
	re.compile(r"\b\d{3}[- ]?\d{2}[- ]?\d{4}\b"),  # US SSN-like
	re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"),  # credit card-like
	re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")  # emails
]

PROFANITY_WORDS = {
	"damn", "shit", "fuck", "bitch", "asshole"
}

INJECTION_CUES = [
	re.compile(r"ignore (?:all|previous) instructions", re.I),
	re.compile(r"disregard (?:the )?system", re.I),
	re.compile(r"pretend you are not", re.I)
]

SENSITIVE_TOPICS = [
	re.compile(r"(?i)political|religion|sex|violence|terror|weapon|suicide|self-harm")
]


def detect_pii(text: str) -> Tuple[bool, str]:
	redacted = text
	found = False
	for pattern in PII_PATTERNS:
		if pattern.search(redacted):
			found = True
			redacted = pattern.sub("[REDACTED]", redacted)
	return found, redacted


def detect_profanity(text: str) -> bool:
	lowered = text.lower()
	return any(word in lowered for word in PROFANITY_WORDS)


def detect_injection(text: str) -> bool:
	return any(p.search(text) for p in INJECTION_CUES)


def detect_sensitive_topics(text: str) -> bool:
	return any(p.search(text) for p in SENSITIVE_TOPICS)


def analyze_guardrails(user_message: str, assistant_response: str) -> dict:
	pii_found_user, redacted_user = detect_pii(user_message)
	pii_found_assistant, redacted_assistant = detect_pii(assistant_response)
	contains_pii = pii_found_user or pii_found_assistant

	contains_profanity = detect_profanity(user_message) or detect_profanity(assistant_response)
	prompt_injection_suspected = detect_injection(user_message)
	contains_sensitive_topics = detect_sensitive_topics(user_message) or detect_sensitive_topics(assistant_response)

	action = "allow"
	message = None
	redacted_text = None
	if contains_pii:
		action = "redact"
		redacted_text = redacted_assistant
		message = "PII detected; returning redacted content."
	elif contains_profanity or prompt_injection_suspected or contains_sensitive_topics:
		action = "warn"
		message = "Potentially unsafe content detected; proceed with caution."

	return {
		"contains_pii": contains_pii,
		"contains_profanity": contains_profanity,
		"prompt_injection_suspected": prompt_injection_suspected,
		"contains_sensitive_topics": contains_sensitive_topics,
		"action": action,
		"message": message,
		"redacted_text": redacted_text,
	}
