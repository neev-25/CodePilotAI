from sqlalchemy.orm import Session

from app.models.analysis_cache import AnalysisCache
from app.models.repository import Repository
from app.models.vector_embedding import VectorEmbedding


class RepositoryRepository:

    @staticmethod
    def create(db: Session, repo: Repository):
        db.add(repo)
        db.commit()
        db.refresh(repo)
        return repo

    @staticmethod
    def get_all(db: Session, user_id: int):
        return db.query(Repository).filter(Repository.user_id == user_id).all()

    @staticmethod
    def get_by_url(db: Session, github_url: str, user_id: int):
        return (
            db.query(Repository)
            .filter(Repository.github_url == github_url, Repository.user_id == user_id)
            .first()
        )

    @staticmethod
    def get_by_id(db: Session, repository_id: int, user_id: int):
        return (
            db.query(Repository)
            .filter(Repository.id == repository_id, Repository.user_id == user_id)
            .first()
        )

    @staticmethod
    def delete(db: Session, repository):
        db.query(AnalysisCache).filter(
            AnalysisCache.repository_id == repository.id
        ).delete(synchronize_session=False)
        db.query(VectorEmbedding).filter(
            VectorEmbedding.repository_id == repository.id
        ).delete(synchronize_session=False)
        db.delete(repository)
        db.commit()