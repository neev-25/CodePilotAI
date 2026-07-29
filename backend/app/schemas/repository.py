from datetime import datetime

from pydantic import BaseModel


class RepositoryCreate(BaseModel):
    github_url: str


class RepositoryResponse(BaseModel):
    id: int
    name: str
    github_url: str
    local_path: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True