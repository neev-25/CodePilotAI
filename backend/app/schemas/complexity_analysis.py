from pydantic import BaseModel


class ComplexFile(BaseModel):
    file: str
    complexity: str
    reason: str


class ComplexityAnalysisResponse(BaseModel):
    overall_score: int
    summary: str
    maintainability: str
    technical_debt: str
    complex_files: list[ComplexFile]
    code_smells: list[str]
    recommendations: list[str]