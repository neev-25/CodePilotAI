from pydantic import BaseModel


class TestGenerationRequest(BaseModel):
    file_path: str


class TestGenerationResponse(BaseModel):
    tests: str