from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint

from app.database.database import Base


class AnalysisCache(Base):
    """A persisted result for an expensive repository analysis operation."""

    __tablename__ = "analysis_cache"
    __table_args__ = (
        UniqueConstraint("repository_id", "artifact_type", "input_key", name="uq_analysis_cache_key"),
    )

    id = Column(Integer, primary_key=True)
    repository_id = Column(Integer, nullable=False, index=True)
    artifact_type = Column(String, nullable=False)
    input_key = Column(String, nullable=False, default="")
    payload = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
