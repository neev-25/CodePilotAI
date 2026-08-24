from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from app.database.database import Base


class IndexingJob(Base):
    __tablename__ = "indexing_jobs"
    id = Column(Integer, primary_key=True)
    repository_id = Column(Integer, nullable=False, index=True)
    status = Column(String, nullable=False, default="QUEUED")
    message = Column(Text, nullable=True)
    result_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
