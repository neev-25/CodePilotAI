from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database.database import Base


class AIUsageLog(Base):
    __tablename__ = "ai_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, nullable=False, index=True)
    service_name = Column(String, nullable=False)
    input_hash = Column(String, nullable=False)
    estimated_tokens = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
