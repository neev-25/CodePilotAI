from pydantic import BaseModel


class RefactoringSuggestion(BaseModel):
    priority: str
    file: str
    reason: str
    recommendation: str


class RefactorResponse(BaseModel):
    overall_score: int
    summary: str
    suggestions: list[RefactoringSuggestion]