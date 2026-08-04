from pydantic import BaseModel


class CommitMessageRequest(BaseModel):
    summary: str


class CommitMessageResponse(BaseModel):
    conventional_commit: str
    detailed_commit: str