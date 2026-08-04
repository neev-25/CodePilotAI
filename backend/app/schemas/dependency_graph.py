from pydantic import BaseModel


class DependencyNode(BaseModel):
    path: str


class DependencyEdge(BaseModel):
    from_file: str
    to_file: str


class DependencyGraphResponse(BaseModel):
    repository: str
    nodes: list[DependencyNode]
    edges: list[DependencyEdge]
    external_dependencies: list[str]