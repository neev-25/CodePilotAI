import json
from typing import List
from app.schemas.response import AskResponse
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.auth import get_current_user
from app.models.user import User
from app.services.indexing_service import IndexingError, IndexingService
from app.core.constants import RepositoryStatus
from app.core.exceptions import (
    RepositoryAlreadyExistsException,
    RepositoryNotFoundException,
)
from app.services.rag_service import RAGService
from app.core.logger import logger
from app.database.dependencies import get_db
from app.models.repository import Repository
from app.repositories.repository_repository import RepositoryRepository
from app.schemas.repository import (
    RepositoryCreate,
    RepositoryResponse,
)
from app.services.git_service import GitService
from app.schemas.ask import AskRequest
from app.services.search_service import SearchService
from app.services.repository_stats_service import RepositoryStatsService
from app.services.repository_summary_service import RepositorySummaryService
from app.schemas.repository_summary import RepositorySummaryResponse
from app.schemas.file_tree import FileTreeResponse
from app.services.file_tree_service import FileTreeService
from app.schemas.dependency_graph import (
    DependencyGraphResponse,
)
from app.services.dependency_graph_service import (
    DependencyGraphService,
)

from app.schemas.dependency_analysis import (
    DependencyAnalysisResponse,
)

from app.services.dependency_analysis_service import (
    DependencyAnalysisService,
)
from app.schemas.documentation import DocumentationResponse
router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"],
    redirect_slashes=False,
)
from app.schemas.file_explain import (
    ExplainFileRequest,
    ExplainFileResponse,
)
from app.services.explain_file_service import (
    ExplainFileService,
)
from app.schemas.function_explain import (
    ExplainFunctionRequest,
    ExplainFunctionResponse,
)
from app.services.function_explain_service import (
    FunctionExplainService,
)
from app.schemas.repository_review import (
    RepositoryReviewResponse,
)

from app.services.repository_review_service import (
    RepositoryReviewService,
)
from app.schemas.security_analysis import (
    SecurityAnalysisResponse,
)

from app.services.security_analysis_service import (
    SecurityAnalysisService,
)
from app.schemas.readme import ReadmeResponse
from app.services.readme_service import ReadmeService
from app.schemas.refactor import (
    RefactorResponse,
)

from app.services.refactor_service import (
    RefactorService,
)
from app.schemas.test_generator import (
    TestGenerationRequest,
    TestGenerationResponse,
)

from app.services.test_generator_service import (
    TestGeneratorService,
)
from app.schemas.pr_description import (
    PRDescriptionRequest,
    PRDescriptionResponse,
)

from app.services.pr_description_service import (
    PRDescriptionService,
)
from app.schemas.commit_message import (
    CommitMessageRequest,
    CommitMessageResponse,
)

from app.services.commit_message_service import (
    CommitMessageService,
)
from app.schemas.changelog import (
    ChangelogRequest,
    ChangelogResponse,
)

from app.services.changelog_service import (
    ChangelogService,
)
from app.schemas.architecture import (
    ArchitectureResponse,
)

from app.services.architecture_service import (
    ArchitectureService,
)
from app.schemas.sequence_diagram import (
    SequenceDiagramResponse,
)
from app.services.sequence_diagram_service import (
    SequenceDiagramService,
)
from app.schemas.class_diagram import (
    ClassDiagramResponse,
)
from app.services.class_diagram_service import (
    ClassDiagramService,
)
from app.schemas.flowchart import (
    FlowchartResponse,
)
from app.services.flowchart_service import (
    FlowchartService,
)
from app.schemas.dependency_analysis import (
    DependencyAnalysisResponse,
)
from app.services.dependency_analysis_service import (
    DependencyAnalysisService,
)
from app.schemas.documentation import (
    DocumentationRequest,
    DocumentationResponse,
)
from app.services.documentation_service import DocumentationService
from app.schemas.complexity_analysis import (
    ComplexityAnalysisResponse,
)

from app.services.complexity_analysis_service import (
    ComplexityAnalysisService,
)
from app.schemas.health_score import (
    RepositoryHealthResponse,
)

from app.services.repository_health_service import (
    RepositoryHealthService,
)
from app.schemas.production_readiness import (
    ProductionReadinessResponse,
)
from app.services.production_readiness_service import (
    ProductionReadinessService,
)
from app.services.semantic_search_service import SemanticSearchService
from app.services.analysis_cache_service import AnalysisCacheService
from app.ai.llm import GeminiServiceError
from app.services.diagram_fallback_service import DiagramFallbackService
from app.models.indexing_job import IndexingJob
from app.services.indexing_job_service import IndexingJobService


def cached_analysis(db, repository, artifact_type, generate, inputs=None, fallback=None):
    try:
        return AnalysisCacheService.get_or_generate(
            db, repository.id, artifact_type, generate, inputs
        )
    except GeminiServiceError as error:
        logger.warning("Gemini failed for repository %s (%s): %s", repository.id, artifact_type, error)
        if fallback:
            # Diagram routes remain useful during provider quota outages.
            return AnalysisCacheService.get_or_generate(
                db, repository.id, artifact_type, fallback, inputs
            )
        raise HTTPException(status_code=502, detail="The AI could not complete this request. Please try again.") from error


def build_health_analysis(db, repository):
    """Compose health reports from persisted sub-analyses instead of re-calling Gemini."""
    analyses = {
        "stats": RepositoryStatsService.get_stats(repository),
        "review": cached_analysis(db, repository, "review", lambda: RepositoryReviewService.review(repository)),
        "security": cached_analysis(db, repository, "security_analysis", lambda: SecurityAnalysisService.analyze(repository)),
        "complexity": cached_analysis(db, repository, "complexity_analysis", lambda: ComplexityAnalysisService.analyze(repository)),
        "dependency": cached_analysis(db, repository, "dependency_analysis", lambda: DependencyAnalysisService.analyze(repository)),
    }
    return RepositoryHealthService.analyze(repository, analyses)
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

    logger.info(f"Cloning repository: {request.github_url}")

    try:
        repo_name, local_path = GitService.clone(request.github_url)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    repo = Repository(
        name=repo_name,
        github_url=request.github_url,
        local_path=local_path,
        status=RepositoryStatus.READY,
        user_id=current_user.id,
    )

    logger.info(f"Repository cloned: {repo_name}")

    return RepositoryRepository.create(
        db,
        repo,
    )


@router.get("", response_model=List[RepositoryResponse])
def list_repositories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    logger.info("Fetching all repositories")

    return RepositoryRepository.get_all(db, current_user.id)


@router.get(
    "/{repository_id}",
    response_model=RepositoryResponse,
)
def get_repository(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    return repository


@router.delete("/{repository_id}")
def delete_repository(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
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
   
@router.post("/{repository_id}/index")
def index_repository(
    repository_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    repository.status = RepositoryStatus.INDEXING
    db.commit()
    db.refresh(repository)

    job = IndexingJob(repository_id=repository.id, status="QUEUED", message="Waiting to begin indexing.")
    db.add(job); db.commit(); db.refresh(job)
    background_tasks.add_task(IndexingJobService.run, job.id, repository.id)
    return {"job_id": job.id, "status": job.status, "message": job.message}


@router.get("/{repository_id}/index-jobs/latest")
def latest_index_job(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify the repo belongs to this user first
    repo = RepositoryRepository.get_by_id(db, repository_id, current_user.id)
    if not repo:
        raise RepositoryNotFoundException()
    job = db.query(IndexingJob).filter(IndexingJob.repository_id == repository_id).order_by(IndexingJob.id.desc()).first()
    if not job:
        raise HTTPException(status_code=404, detail="No indexing job found.")
    return {"id": job.id, "status": job.status, "message": job.message, "result": json.loads(job.result_json) if job.result_json else None}

@router.post("/{repository_id}/ask", response_model=AskResponse)
def ask_repository(
    repository_id: int,
    request: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(status_code=400, detail="Repository has not been indexed yet.")

    return RAGService.ask(
        request.question,
        repository_id,
    )

@router.get("/{repository_id}/stats")
def repository_stats(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    return RepositoryStatsService.get_stats(
        repository,
    )
    
@router.post("/{repository_id}/summary",
    response_model=RepositorySummaryResponse,
)
def repository_summary(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "summary", lambda: RepositorySummaryService.generate_summary(repository))
    
@router.get(
    "/{repository_id}/files",
    response_model=FileTreeResponse,
)
def repository_files(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    return FileTreeService.get_tree(
        repository
    )
    
@router.post("/{repository_id}/search")
def semantic_search(
    repository_id: int,
    request: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return SemanticSearchService.search(repository_id, request.question)

@router.post(
    "/{repository_id}/files/explain",
    response_model=ExplainFileResponse,
)
def explain_file(
    repository_id: int,
    request: ExplainFileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "file_explanation", lambda: ExplainFileService.explain(repository, request.path), {"path": request.path})
    
@router.post(
    "/{repository_id}/functions/explain",
    response_model=ExplainFunctionResponse,
)
def explain_function(
    repository_id: int,
    request: ExplainFunctionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "function_explanation", lambda: FunctionExplainService.explain(repository, request.path, request.function), {"path": request.path, "function": request.function})
    
@router.get(
    "/{repository_id}/dependencies",
    response_model=DependencyGraphResponse,
)
def dependency_graph(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "dependency_graph", lambda: DependencyGraphService.build(repository))
    
@router.post(
    "/{repository_id}/review",
    response_model=RepositoryReviewResponse,
)
def review_repository(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "review", lambda: RepositoryReviewService.review(repository))
    
@router.post(
    "/{repository_id}/security-analysis",
    response_model=SecurityAnalysisResponse,
)
def security_analysis(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "security_analysis", lambda: SecurityAnalysisService.analyze(repository))
    
@router.post(
    "/{repository_id}/files/document",
    response_model=DocumentationResponse,
)
def generate_documentation(
    repository_id: int,
    request: DocumentationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "documentation", lambda: DocumentationService.generate(repository, request.file_path), {"path": request.file_path})
    
@router.post(
    "/{repository_id}/readme",
    response_model=ReadmeResponse,
)
def generate_readme(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "readme", lambda: ReadmeService.generate(repository))

@router.post(
    "/{repository_id}/refactor",
    response_model=RefactorResponse,
)
def generate_refactor(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "refactor", lambda: RefactorService.generate(repository))

@router.post(
    "/{repository_id}/files/tests",
    response_model=TestGenerationResponse,
)
def generate_tests(
    repository_id: int,
    request: TestGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "tests", lambda: TestGeneratorService.generate(repository, request.file_path), {"path": request.file_path})
    
@router.post(
    "/{repository_id}/pr-description",
    response_model=PRDescriptionResponse,
)
def generate_pr_description(
    repository_id: int,
    request: PRDescriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "pr_description", lambda: PRDescriptionService.generate(repository, request.title, request.summary), {"title": request.title, "summary": request.summary})
    
@router.post(
    "/{repository_id}/commit-message",
    response_model=CommitMessageResponse,
)
def generate_commit_message(
    repository_id: int,
    request: CommitMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "commit_message", lambda: CommitMessageService.generate(repository, request.summary), {"summary": request.summary})
    
@router.post(
    "/{repository_id}/changelog",
    response_model=ChangelogResponse,
)
def generate_changelog(
    repository_id: int,
    request: ChangelogRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "changelog", lambda: ChangelogService.generate(repository, request.version, request.summary), {"version": request.version, "summary": request.summary})
    
@router.post(
    "/{repository_id}/architecture",
    response_model=ArchitectureResponse,
)
def generate_architecture(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "architecture", lambda: ArchitectureService.generate(repository))
    
@router.post(
    "/{repository_id}/sequence-diagram",
    response_model=SequenceDiagramResponse,
)
def generate_sequence_diagram(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "sequence_diagram", lambda: SequenceDiagramService.generate(repository), fallback=lambda: DiagramFallbackService.sequence(repository))
    
@router.post(
    "/{repository_id}/class-diagram",
    response_model=ClassDiagramResponse,
)
def generate_class_diagram(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "class_diagram", lambda: ClassDiagramService.generate(repository), fallback=lambda: DiagramFallbackService.class_diagram(repository))
    
@router.post(
    "/{repository_id}/flowchart",
    response_model=FlowchartResponse,
)
def generate_flowchart(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "flowchart", lambda: FlowchartService.generate(repository), fallback=lambda: DiagramFallbackService.flowchart(repository))
    
@router.post(
    "/{repository_id}/dependency-analysis",
    response_model=DependencyAnalysisResponse,
)
def dependency_analysis(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "dependency_analysis", lambda: DependencyAnalysisService.analyze(repository))
    
@router.post(
    "/{repository_id}/complexity-analysis",
    response_model=ComplexityAnalysisResponse,
)
def complexity_analysis(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "complexity_analysis", lambda: ComplexityAnalysisService.analyze(repository))
    
@router.post(
    "/{repository_id}/health-score",
    response_model=RepositoryHealthResponse,
)
def repository_health(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return cached_analysis(db, repository, "health_score", lambda: build_health_analysis(db, repository))
@router.post(
    "/{repository_id}/production-readiness",
    response_model=ProductionReadinessResponse,
)
def production_readiness(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
        current_user.id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    health = cached_analysis(db, repository, "health_score", lambda: build_health_analysis(db, repository))
    return cached_analysis(db, repository, "production_readiness", lambda: ProductionReadinessService.analyze(repository, health))

