from pydantic import BaseModel


class DocumentationRequest(BaseModel):
    file_path: str

class DocumentationResponse(BaseModel):
    markdown: str

class DiffReviewRequest(BaseModel):
    diff_text: str

class DiffReviewResponse(BaseModel):
    review: str

class ChangeImpactRequest(BaseModel):
    file_path: str
    proposed_change: str

class ChangeImpactResponse(BaseModel):
    impact: str


class DocumentationResponse(BaseModel):
    documentation: str