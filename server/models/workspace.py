"""Workspace model — per-user isolated research space."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return uuid.uuid4().hex[:16]


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String(16), primary_key=True, default=_new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), default="My Workspace")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    # relationships
    owner: Mapped["User"] = relationship("User", back_populates="workspaces")
    conversations: Mapped[list["Conversation"]] = relationship("Conversation", back_populates="workspace", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Workspace {self.name} (user={self.user_id})>"
