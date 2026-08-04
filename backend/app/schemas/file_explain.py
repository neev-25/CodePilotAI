from pydantic import BaseModel


class ExplainFileRequest(BaseModel):
    path: str


class ExplainFileResponse(BaseModel):
    file: str
    explanation: str