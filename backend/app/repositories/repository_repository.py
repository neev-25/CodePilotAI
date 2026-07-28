from sqlalchemy.orm import Session

from app.models.repository import Repository


class RepositoryRepository:

    @staticmethod
    def create(db: Session, repo: Repository):

        db.add(repo)

        db.commit()

        db.refresh(repo)

        return repo

    @staticmethod
    def get_all(db: Session):

        return db.query(Repository).all()