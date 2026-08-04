from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class FileNode(BaseModel):
    name: str
    type: str
    children: Optional[List["FileNode"]] = None


FileNode.model_rebuild()


class FileTreeResponse(BaseModel):
    repository: str
    tree: List[FileNode]