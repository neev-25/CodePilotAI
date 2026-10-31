from sqlalchemy import Column, Index, Integer, JSON, String, Text
from pgvector.sqlalchemy import Vector

from app.database.database import Base

EMBEDDING_DIMENSIONS = 3072


class VectorEmbedding(Base):
    __tablename__ = "repository_embeddings"
    __table_args__ = (
        Index("ix_repository_embeddings_repository_path", "repository_id", "path"),
    )

    id = Column(String(128), primary_key=True)
    repository_id = Column(Integer, nullable=False)
    path = Column(String, nullable=False)
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(
        Vector(EMBEDDING_DIMENSIONS).with_variant(JSON(), "sqlite"),
        nullable=False,
    )
