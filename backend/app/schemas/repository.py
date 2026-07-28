from pydantic import BaseModel


class RepositoryCreate(BaseModel):
    github_url: str


class RepositoryResponse(BaseModel):
    id: int
    name: str
    github_url: str
    status: str

    class Config:
        from_attributes = True