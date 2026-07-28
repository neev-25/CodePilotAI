from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database.database import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    github_url = Column(String, nullable=False, unique=True)

    local_path = Column(String, nullable=False)

    status = Column(String, default="PENDING")

    created_at = Column(DateTime, default=datetime.utcnow)