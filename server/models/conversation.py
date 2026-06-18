"""Conversation model — research goal, config, and log entries."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Text, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return uuid.uuid4().hex[:16]


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(16), primary_key=True, default=_new_id)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), default="Untitled Research")
    goal: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft / running / completed / failed
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    token_usage: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)

    # relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="conversations")
    logs: Mapped[list["ConversationLog"]] = relationship("ConversationLog", back_populates="conversation", cascade="all, delete-orphan", order_by="ConversationLog.seq")

    def __repr__(self):
        return f"<Conversation {self.title}>"


class ConversationLog(Base):
    __tablename__ = "conversation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    seq: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    # relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="logs")

    def __repr__(self):
        return f"<ConversationLog #{self.seq}>"
