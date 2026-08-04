from pydantic import BaseModel, Field


class DependencyEdge(BaseModel):
    from_file: str = Field(alias="from")
    to_file: str = Field(alias="to")

    model_config = {
        "populate_by_name": True
    }


class CoupledModule(BaseModel):
    module: str
    reason: str


class DependencyAnalysisResponse(BaseModel):
    overall_score: int

    summary: str

    internal_dependencies: list[DependencyEdge]

    external_dependencies: list[str]

    circular_dependencies: list[list[str]]

    highly_coupled_modules: list[CoupledModule]

    recommendations: list[str]