from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.repository import (
    RepositoryCreate,
    RepositoryResponse,
)
from app.models.repository import Repository
from app.repositories.repository_repository import RepositoryRepository
from app.services.git_service import GitService
from typing import List

router = APIRouter(prefix="/repositories", tags=["Repositories"])


@router.post("/", response_model=RepositoryResponse)
def create_repository(
    request: RepositoryCreate,
    db: Session = Depends(get_db),
):
    repo_name, local_path = GitService.clone(request.github_url)

    repo = Repository(
        name=repo_name,
        github_url=request.github_url,
        local_path=local_path,
        status="READY",
    )

    return RepositoryRepository.create(db, repo)


@router.get("/", response_model=List[RepositoryResponse])
def list_repositories(db: Session = Depends(get_db)):
    return RepositoryRepository.get_all(db)