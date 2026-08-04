from typing import List
from app.schemas.response import AskResponse
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.services.indexing_service import IndexingService
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
   
@router.post("/{repository_id}/index")
def index_repository(
    repository_id: int,
    db: Session = Depends(get_db),
):
    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    repository.status = RepositoryStatus.INDEXING
    db.commit()
    db.refresh(repository)

    try:
        result = IndexingService.index(
            repository_id=repository.id,
            repository_path=repository.local_path,
        )

        repository.status = RepositoryStatus.INDEXED
        db.commit()
        db.refresh(repository)

        return {
            "message": "Repository indexed successfully.",
            "stats": result,
        }

    except Exception:
        repository.status = RepositoryStatus.FAILED
        db.commit()
        db.refresh(repository)
        raise 

@router.post("/{repository_id}/ask", response_model=AskResponse)
def ask_repository(
    repository_id: int,
    request: AskRequest,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise Exception("Repository has not been indexed yet.")

    return RAGService.ask(
        request.question,
        repository_id,
    )

@router.get("/{repository_id}/stats")
def repository_stats(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    return RepositoryStatsService.get_stats(
        repository,
    )
    
@router.post(
    "/{repository_id}/summary",
    response_model=RepositorySummaryResponse,
)
def repository_summary(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return RepositorySummaryService.generate_summary(
        repository
    )
    
@router.get(
    "/{repository_id}/files",
    response_model=FileTreeResponse,
)
def repository_files(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    return FileTreeService.get_tree(
        repository
    )
    
@router.post(
    "/{repository_id}/files/explain",
    response_model=ExplainFileResponse,
)
def explain_file(
    repository_id: int,
    request: ExplainFileRequest,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return ExplainFileService.explain(
        repository,
        request.path,
    )
    
@router.post(
    "/{repository_id}/functions/explain",
    response_model=ExplainFunctionResponse,
)
def explain_function(
    repository_id: int,
    request: ExplainFunctionRequest,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return FunctionExplainService.explain(
        repository,
        request.path,
        request.function,
    )
    
@router.get(
    "/{repository_id}/dependencies",
    response_model=DependencyGraphResponse,
)
def dependency_graph(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return DependencyGraphService.build(
        repository
    )
    
@router.post(
    "/{repository_id}/review",
    response_model=RepositoryReviewResponse,
)
def review_repository(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return RepositoryReviewService.review(
        repository
    )
    
@router.post(
    "/{repository_id}/security-analysis",
    response_model=SecurityAnalysisResponse,
)
def security_analysis(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return SecurityAnalysisService.analyze(
        repository
    )
    
@router.post(
    "/{repository_id}/files/document",
    response_model=DocumentationResponse,
)
def generate_documentation(
    repository_id: int,
    request: DocumentationRequest,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return DocumentationService.generate(
        repository,
        request.file_path,
    )
    
@router.post(
    "/{repository_id}/readme",
    response_model=ReadmeResponse,
)
def generate_readme(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return ReadmeService.generate(repository)

@router.post(
    "/{repository_id}/refactor",
    response_model=RefactorResponse,
)
def generate_refactor(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return RefactorService.generate(repository)

@router.post(
    "/{repository_id}/files/tests",
    response_model=TestGenerationResponse,
)
def generate_tests(
    repository_id: int,
    request: TestGenerationRequest,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return TestGeneratorService.generate(
        repository,
        request.file_path,
    )
    
@router.post(
    "/{repository_id}/pr-description",
    response_model=PRDescriptionResponse,
)
def generate_pr_description(
    repository_id: int,
    request: PRDescriptionRequest,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return PRDescriptionService.generate(
        repository,
        request.title,
        request.summary,
    )
    
@router.post(
    "/{repository_id}/commit-message",
    response_model=CommitMessageResponse,
)
def generate_commit_message(
    repository_id: int,
    request: CommitMessageRequest,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return CommitMessageService.generate(
        repository,
        request.summary,
    )
    
@router.post(
    "/{repository_id}/changelog",
    response_model=ChangelogResponse,
)
def generate_changelog(
    repository_id: int,
    request: ChangelogRequest,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return ChangelogService.generate(
        repository,
        request.version,
        request.summary,
    )
    
@router.post(
    "/{repository_id}/architecture",
    response_model=ArchitectureResponse,
)
def generate_architecture(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return ArchitectureService.generate(
        repository,
    )
    
@router.post(
    "/{repository_id}/sequence-diagram",
    response_model=SequenceDiagramResponse,
)
def generate_sequence_diagram(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return SequenceDiagramService.generate(
        repository,
    )
    
@router.post(
    "/{repository_id}/class-diagram",
    response_model=ClassDiagramResponse,
)
def generate_class_diagram(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return ClassDiagramService.generate(
        repository,
    )
    
@router.post(
    "/{repository_id}/flowchart",
    response_model=FlowchartResponse,
)
def generate_flowchart(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return FlowchartService.generate(
        repository,
    )
    
@router.post(
    "/{repository_id}/dependency-analysis",
    response_model=DependencyAnalysisResponse,
)
def dependency_analysis(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return DependencyAnalysisService.analyze(
        repository
    )
    
@router.post(
    "/{repository_id}/dependency-analysis",
    response_model=DependencyAnalysisResponse,
)
def dependency_analysis(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return DependencyAnalysisService.analyze(
        repository
    )
    
@router.post(
    "/{repository_id}/complexity-analysis",
    response_model=ComplexityAnalysisResponse,
)
def complexity_analysis(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return ComplexityAnalysisService.analyze(
        repository
    )
    
@router.post(
    "/{repository_id}/health-score",
    response_model=RepositoryHealthResponse,
)
def repository_health(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return RepositoryHealthService.analyze(
        repository
    )
@router.post(
    "/{repository_id}/production-readiness",
    response_model=ProductionReadinessResponse,
)
def production_readiness(
    repository_id: int,
    db: Session = Depends(get_db),
):

    repository = RepositoryRepository.get_by_id(
        db,
        repository_id,
    )

    if not repository:
        raise RepositoryNotFoundException()

    if repository.status != RepositoryStatus.INDEXED:
        raise HTTPException(
            status_code=400,
            detail="Repository has not been indexed.",
        )

    return ProductionReadinessService.analyze(
        repository
    )