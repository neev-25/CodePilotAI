import json
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.llm import GeminiServiceError
from app.api.auth import get_current_user
from app.core.constants import RepositoryStatus
from app.core.exceptions import (
    RepositoryAlreadyExistsException,
    RepositoryNotFoundException,
)
from app.core.logger import logger
from app.database.dependencies import get_db
from app.models.indexing_job import IndexingJob
from app.models.repository import Repository
from app.models.user import User
from app.repositories.repository_repository import RepositoryRepository
from app.schemas.ask import AskRequest
from app.schemas.dependency_graph import DependencyGraphResponse
from app.schemas.diagram import DiagramResponse
from app.schemas.health_score import RepositoryHealthResponse
from app.schemas.project_assessment import ProjectAssessmentResponse
from app.schemas.production_readiness import ProductionReadinessResponse
from app.schemas.repository import RepositoryCreate, RepositoryResponse
from app.schemas.response import AskResponse
from app.schemas.security_analysis import SecurityAnalysisResponse
from app.schemas.test_generator import TestGenerationRequest, TestGenerationResponse
from app.services.analysis_cache_service import AnalysisCacheService
from app.services.class_diagram_service import ClassDiagramService
from app.services.complexity_analysis_service import ComplexityAnalysisService
from app.services.dependency_analysis_service import DependencyAnalysisService
from app.services.dependency_graph_service import DependencyGraphService
from app.services.flowchart_service import FlowchartService
from app.services.file_tree_service import FileTreeService
from app.services.git_service import GitService
from app.services.indexing_job_service import IndexingJobService
from app.services.indexing_service import IndexingError, IndexingService
from app.services.onboarding_service import OnboardingService
from app.services.project_assessment_service import (
    ProjectAssessmentError,
    ProjectAssessmentService,
)
from app.services.production_readiness_service import (
    ProductionReadinessError,
    ProductionReadinessService,
)
from app.services.rag_service import RAGService
from app.services.repository_diagram_service import DiagramGenerationError
from app.services.repository_health_service import RepositoryHealthService
from app.services.repository_review_service import RepositoryReviewService
from app.services.repository_stats_service import RepositoryStatsService
from app.services.security_analysis_service import SecurityAnalysisService
from app.services.sequence_diagram_service import SequenceDiagramService
from app.services.test_generator_service import (
    InvalidTestSourceError,
    TestGenerationError,
    TestGeneratorService,
)
from app.schemas.file_tree import FileTreeResponse
from app.schemas.deep_analytics import OnboardingResponse

router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"],
    redirect_slashes=False,
)


def cached_analysis(db, repository, artifact_type, generate, inputs=None):
    try:
        return AnalysisCacheService.get_or_generate(
            db, repository.id, artifact_type, generate, inputs
        )
    except GeminiServiceError as error:
        logger.warning(
            "Gemini failed for repository %s (%s): %s",
            repository.id,
            artifact_type,
            error,
        )
        raise HTTPException(
            status_code=502,
            detail="The AI could not complete this request. Please try again.",
        ) from error


def build_health_analysis(db, repository):
    analyses = {
        "stats": RepositoryStatsService.get_stats(repository),
        "review": cached_analysis(
            db,
            repository,
            "review",
            lambda: RepositoryReviewService.review(repository),
        ),
        "security": cached_analysis(
            db,
            repository,
            "security_analysis",
            lambda: SecurityAnalysisService.analyze(repository),
        ),
        "complexity": cached_analysis(
            db,
            repository,
            "complexity_analysis",
            lambda: ComplexityAnalysisService.analyze(repository),
        ),
        "dependency": cached_analysis(
            db,
            repository,
            "dependency_analysis",
            lambda: DependencyAnalysisService.analyze(repository),
        ),
    }
    return RepositoryHealthService.analyze(repository, analyses)


def get_owned_repository(
    repository_id: int,
    db: Session,
    current_user: User,
) -> Repository:
    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )
    if not repository:
        raise RepositoryNotFoundException()
    return repository


def require_indexed(repository: Repository) -> None:
    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )


@router.post("", response_model=RepositoryResponse)
def create_repository(
    request: RepositoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = RepositoryRepository.get_by_url(
        db,
        request.github_url,
        current_user.id,
    )
    if existing:
        raise RepositoryAlreadyExistsException()

    logger.info("Cloning repository: %s", request.github_url)
    try:
        repo_name, local_path = GitService.clone(request.github_url)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    repository = Repository(
        name=repo_name,
        github_url=request.github_url,
        local_path=local_path,
        status=RepositoryStatus.READY,
        user_id=current_user.id,
    )
    return RepositoryRepository.create(db, repository)


@router.get("", response_model=list[RepositoryResponse])
def list_repositories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return RepositoryRepository.get_all(db, current_user.id)


@router.get("/{repository_id}", response_model=RepositoryResponse)
def get_repository(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_owned_repository(repository_id, db, current_user)


@router.delete("/{repository_id}")
def delete_repository(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = get_owned_repository(repository_id, db, current_user)
    RepositoryRepository.delete(db, repository)
    logger.info("Deleted repository %s", repository.name)
    return {"message": "Repository deleted."}


@router.post("/{repository_id}/index")
def index_repository(
    repository_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = (
        db.query(Repository)
        .filter(
            Repository.id == repository_id,
            Repository.user_id == current_user.id,
        )
        .with_for_update()
        .first()
    )
    if not repository:
        raise RepositoryNotFoundException()

    active_job = (
        db.query(IndexingJob)
        .filter(
            IndexingJob.repository_id == repository.id,
            IndexingJob.status.in_(("QUEUED", "RUNNING", "RETRYING")),
        )
        .order_by(IndexingJob.id.desc())
        .first()
    )
    if active_job:
        return {
            "job_id": active_job.id,
            "status": active_job.status,
            "message": active_job.message or "Repository indexing is already in progress.",
        }

    repository.status = RepositoryStatus.INDEXING
    job = IndexingJob(
        repository_id=repository.id,
        status="QUEUED",
        message="Waiting to begin indexing.",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    db.refresh(repository)
    background_tasks.add_task(IndexingJobService.run, job.id, repository.id)
    return {"job_id": job.id, "status": job.status, "message": job.message}


@router.get("/{repository_id}/index-jobs/latest")
def latest_index_job(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_repository(repository_id, db, current_user)
    job = (
        db.query(IndexingJob)
        .filter(IndexingJob.repository_id == repository_id)
        .order_by(IndexingJob.id.desc())
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="No indexing job found.")
    return {
        "id": job.id,
        "status": job.status,
        "message": job.message,
        "result": json.loads(job.result_json) if job.result_json else None,
    }


@router.post("/{repository_id}/ask", response_model=AskResponse)
def ask_repository(
    repository_id: int,
    request: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = get_owned_repository(repository_id, db, current_user)
    require_indexed(repository)
    return cached_analysis(
        db,
        repository,
        "repository_question",
        lambda: RAGService.ask(request.question, repository.id),
        inputs={"question": request.question},
    )


@router.post(
    "/{repository_id}/assessment",
    response_model=ProjectAssessmentResponse,
)
def project_assessment(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = get_owned_repository(repository_id, db, current_user)
    require_indexed(repository)
    try:
        return cached_analysis(
            db,
            repository,
            "project_assessment",
            lambda: ProjectAssessmentService.generate(repository),
        )
    except ProjectAssessmentError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post(
    "/{repository_id}/sequence-diagram",
    response_model=DiagramResponse,
)
def sequence_diagram(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = get_owned_repository(repository_id, db, current_user)
    require_indexed(repository)
    try:
        return cached_analysis(
            db,
            repository,
            "sequence_diagram",
            lambda: SequenceDiagramService.generate(repository),
        )
    except DiagramGenerationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post(
    "/{repository_id}/class-diagram",
    response_model=DiagramResponse,
)
def class_diagram(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = get_owned_repository(repository_id, db, current_user)
    require_indexed(repository)
    try:
        return cached_analysis(
            db,
            repository,
            "class_diagram",
            lambda: ClassDiagramService.generate(repository),
        )
    except DiagramGenerationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post(
    "/{repository_id}/flowchart",
    response_model=DiagramResponse,
)
def repository_flowchart(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = get_owned_repository(repository_id, db, current_user)
    require_indexed(repository)
    try:
        return cached_analysis(
            db,
            repository,
            "flowchart",
            lambda: FlowchartService.generate(repository),
        )
    except DiagramGenerationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post(
    "/{repository_id}/production-readiness",
    response_model=ProductionReadinessResponse,
)
def production_readiness(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = get_owned_repository(repository_id, db, current_user)
    require_indexed(repository)
    try:
        return cached_analysis(
            db,
            repository,
            "production_readiness",
            lambda: ProductionReadinessService.analyze(
                repository,
                build_health_analysis(db, repository),
            ),
        )
    except ProductionReadinessError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


@router.post(
    "/{repository_id}/test-cases",
    response_model=TestGenerationResponse,
)
def generate_test_cases(
    repository_id: int,
    request: TestGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = get_owned_repository(repository_id, db, current_user)
    require_indexed(repository)
    try:
        return cached_analysis(
            db,
            repository,
            "test_cases",
            lambda: TestGeneratorService.generate(repository, request.file_path),
            inputs={"file_path": request.file_path},
        )
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except InvalidTestSourceError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except TestGenerationError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


@router.get("/{repository_id}/stats")
def repository_stats(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = get_owned_repository(repository_id, db, current_user)
    return RepositoryStatsService.get_stats(repository)


@router.get("/{repository_id}/files", response_model=FileTreeResponse)
def repository_files(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = get_owned_repository(repository_id, db, current_user)
    return FileTreeService.get_tree(repository)


@router.get("/{repository_id}/files/content")
def repository_file_content(
    repository_id: int,
    file_path: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = get_owned_repository(repository_id, db, current_user)
    root = Path(repository.local_path).resolve()
    target = (root / file_path).resolve()
    if target != root and root not in target.parents:
        raise HTTPException(status_code=400, detail="Invalid repository file path.")
    if not target.is_file():
        raise HTTPException(status_code=404, detail="Repository file not found.")
    if target.stat().st_size > 1_000_000:
        raise HTTPException(status_code=413, detail="Repository file is too large to display.")

    content = target.read_bytes()
    if b"\x00" in content:
        raise HTTPException(status_code=415, detail="Binary files cannot be displayed.")
    return {
        "path": target.relative_to(root).as_posix(),
        "content": content.decode("utf-8", errors="replace"),
    }


@router.get(
    "/{repository_id}/dependencies",
    response_model=DependencyGraphResponse,
)
def dependency_graph(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = get_owned_repository(repository_id, db, current_user)
    require_indexed(repository)
    return cached_analysis(
        db,
        repository,
        "dependency_graph",
        lambda: DependencyGraphService.build(repository),
    )


@router.post(
    "/{repository_id}/security-analysis",
    response_model=SecurityAnalysisResponse,
)
def security_analysis(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = get_owned_repository(repository_id, db, current_user)
    require_indexed(repository)
    return cached_analysis(
        db,
        repository,
        "security_analysis",
        lambda: SecurityAnalysisService.analyze(repository),
    )


@router.post(
    "/{repository_id}/health-score",
    response_model=RepositoryHealthResponse,
)
def repository_health(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = get_owned_repository(repository_id, db, current_user)
    require_indexed(repository)
    return cached_analysis(
        db,
        repository,
        "health_score",
        lambda: build_health_analysis(db, repository),
    )


@router.post(
    "/{repository_id}/onboarding",
    response_model=OnboardingResponse,
)
def generate_onboarding(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = get_owned_repository(repository_id, db, current_user)
    require_indexed(repository)
    return cached_analysis(
        db,
        repository,
        "onboarding",
        lambda: OnboardingService.generate(repository),
    )
