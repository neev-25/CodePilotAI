from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from datetime import datetime
import enum

from app.database.database import Base

class TaskStatus(enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.OPEN)
    created_at = Column(DateTime, default=datetime.utcnow)
