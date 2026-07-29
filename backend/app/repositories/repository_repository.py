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
    
    @staticmethod
    def get_by_url(db: Session, github_url: str):

        return (
            db.query(Repository)
            .filter(Repository.github_url == github_url)
            .first()
        )
        
    @staticmethod
    def get_by_id(
            db: Session,
            repository_id: int,
        ):
            return (
                db.query(Repository)
                .filter(Repository.id == repository_id)
                .first()
        )
            
    @staticmethod
    def delete(
        db: Session,
        repository,
    ):
        db.delete(repository)
        db.commit()