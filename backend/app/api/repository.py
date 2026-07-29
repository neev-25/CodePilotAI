from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import RepositoryStatus
from app.core.exceptions import (
    RepositoryAlreadyExistsException,
    RepositoryNotFoundException,
)
from app.core.logger import logger
from app.database.dependencies import get_db
from app.models.repository import Repository
from app.repositories.repository_repository import RepositoryRepository
from app.schemas.repository import (
    RepositoryCreate,
    RepositoryResponse,
)
from app.services.git_service import GitService

router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"],
)


@router.post("/", response_model=RepositoryResponse)
def create_repository(
    request: RepositoryCreate,
    db: Session = Depends(get_db),
):

    existing = RepositoryRepository.get_by_url(
        db,
        request.github_url,
    )

    if existing:
        raise RepositoryAlreadyExistsException()

    logger.info(f"Cloning repository: {request.github_url}")

    repo_name, local_path = GitService.clone(
        request.github_url,
    )

    repo = Repository(
        name=repo_name,
        github_url=request.github_url,
        local_path=local_path,
        status=RepositoryStatus.READY,
    )

    logger.info(f"Repository cloned: {repo_name}")

    return RepositoryRepository.create(
        db,
        repo,
    )


@router.get("/", response_model=List[RepositoryResponse])
def list_repositories(
    db: Session = Depends(get_db),
):

    logger.info("Fetching all repositories")

    return RepositoryRepository.get_all(db)


@router.get(
    "/{repository_id}",
    response_model=RepositoryResponse,
)
def get_repository(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    return repository


@router.delete("/{repository_id}")
def delete_repository(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    RepositoryRepository.delete(
        db,
        repository,
    )

    logger.info(
        f"Deleted repository {repository.name}"
    )

    return {
        "message": "Repository deleted."
    }