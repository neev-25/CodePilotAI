import re

from pydantic import BaseModel
from pydantic import Field, field_validator


class TestGenerationRequest(BaseModel):
    file_path: str


class GeneratedTestCase(BaseModel):
    name: str
    category: str
    purpose: str
    expected_result: str


class TestGenerationResponse(BaseModel):
    source_file: str
    test_file_path: str
    framework: str
    summary: str
    test_cases: list[GeneratedTestCase] = Field(min_length=1)
    test_code: str = Field(min_length=20)

    @field_validator("test_code")
    @classmethod
    def require_assertions(cls, code: str) -> str:
        if not re.search(
            r"\bassert\w*\s*(?:\(|\b)|\bexpect\s*\(|\bt\.(?:Error|Fatal)\s*\("
            r"|\bShould[A-Z]|\bassert_eq!\s*\(",
            code,
        ):
            raise ValueError("Generated test code must contain real assertions.")
        if re.search(
            r"\bTODO\b|assert\s+True\b|assert\s+true\b|assertTrue\(\s*true\s*\)"
            r"|expect\(\s*true\s*\)",
            code,
            flags=re.IGNORECASE,
        ):
            raise ValueError("Generated test code contains placeholder assertions.")
        return code
