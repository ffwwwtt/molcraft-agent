"""ExperimentRecord model — per-iteration experiment results."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Integer, Float, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class ExperimentRecord(Base):
    __tablename__ = "experiment_records"

    id: Mapped[str] = mapped_column(String(16), primary_key=True, default=lambda: uuid.uuid4().hex[:16])
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id: Mapped[str | None] = mapped_column(ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True, index=True)
    round_num: Mapped[int] = mapped_column(Integer, default=0)
    hypothesis: Mapped[str | None] = mapped_column(default=None)
    method: Mapped[str | None] = mapped_column(default=None)
    conclusion: Mapped[str | None] = mapped_column(default=None)
    success: Mapped[bool | None] = mapped_column(Boolean, default=None)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    chart_files: Mapped[list] = mapped_column(JSON, default=list)
    record_type: Mapped[str] = mapped_column(String(20), default="experiment")  # "experiment" or "report"
    timestamp: Mapped[str | None] = mapped_column(String(64), default=None)  # ISO timestamp from agent
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
