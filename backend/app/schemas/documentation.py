from pydantic import BaseModel


class DocumentationRequest(BaseModel):
    file_path: str

class DocumentationResponse(BaseModel):
    markdown: str

class DiffReviewRequest(BaseModel):
    diff_text: str

class DiffReviewResponse(BaseModel):
    review: str


class DocumentationResponse(BaseModel):
    documentation: str