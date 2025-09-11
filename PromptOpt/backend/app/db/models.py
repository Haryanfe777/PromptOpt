from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class User(Base):
	__tablename__ = "users"
	id = Column(Integer, primary_key=True, index=True)
	username = Column(String(100), unique=True, nullable=False, index=True)
	password_hash = Column(String(255), nullable=False)
	role = Column(String(20), nullable=False, index=True)  # 'admin' or 'employee'
	created_at = Column(DateTime, default=datetime.utcnow)

	conversations = relationship("Conversation", back_populates="user")


class Prompt(Base):
	__tablename__ = "prompts"
	id = Column(Integer, primary_key=True, index=True)
	title = Column(String(200), nullable=False)
	created_by = Column(String(100), nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)

	versions = relationship("PromptVersion", back_populates="prompt")


class PromptVersion(Base):
	__tablename__ = "prompt_versions"
	id = Column(Integer, primary_key=True, index=True)
	prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
	version = Column(Integer, nullable=False)
	content = Column(Text, nullable=False)
	is_active = Column(Boolean, default=True)
	created_at = Column(DateTime, default=datetime.utcnow)

	prompt = relationship("Prompt", back_populates="versions")
	conversations = relationship("Conversation", back_populates="prompt_version")


class Conversation(Base):
	__tablename__ = "conversations"
	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	prompt_version_id = Column(Integer, ForeignKey("prompt_versions.id"), nullable=True)
	started_at = Column(DateTime, default=datetime.utcnow)

	user = relationship("User", back_populates="conversations")
	prompt_version = relationship("PromptVersion", back_populates="conversations")
	messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
	evaluations = relationship("Evaluation", back_populates="conversation", cascade="all, delete-orphan")
	guardrails = relationship("Guardrail", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
	__tablename__ = "messages"
	id = Column(Integer, primary_key=True, index=True)
	conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
	role = Column(String(20), nullable=False)  # 'user' | 'assistant'
	content = Column(Text, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)

	conversation = relationship("Conversation", back_populates="messages")


class Evaluation(Base):
	__tablename__ = "evaluations"
	id = Column(Integer, primary_key=True, index=True)
	conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
	message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
	overall = Column(Float, nullable=False)
	criteria = Column(JSON, nullable=False)
	label = Column(String(50), nullable=True)
	judge_model = Column(String(100), nullable=True)
	created_at = Column(DateTime, default=datetime.utcnow)

	conversation = relationship("Conversation", back_populates="evaluations")


class Guardrail(Base):
	__tablename__ = "guardrails"
	id = Column(Integer, primary_key=True, index=True)
	conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
	message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
	action = Column(String(20), nullable=False)  # allow | warn | redact | block
	report = Column(JSON, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)

	conversation = relationship("Conversation", back_populates="guardrails")
