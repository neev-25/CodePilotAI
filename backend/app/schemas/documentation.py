from pydantic import BaseModel


class DocumentationRequest(BaseModel):
    file_path: str


class DocumentationResponse(BaseModel):
    documentation: str