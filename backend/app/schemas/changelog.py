from pydantic import BaseModel


class ChangelogRequest(BaseModel):
    version: str
    summary: str


class ChangelogResponse(BaseModel):
    changelog: str