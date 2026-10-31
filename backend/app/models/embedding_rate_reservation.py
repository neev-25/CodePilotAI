from datetime import datetime

from sqlalchemy import Column, DateTime, Integer

from app.database.database import Base


class EmbeddingRateReservation(Base):
    """Shared token reservations for all backend processes using this database."""

    __tablename__ = "embedding_rate_reservations"

    id = Column(Integer, primary_key=True)
    estimated_tokens = Column(Integer, nullable=False)
    reserved_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
