from types import SimpleNamespace

import pytest

from app.services.project_assessment_service import (
    ProjectAssessmentError,
    ProjectAssessmentService,
)
from app.services.search_service import SearchService


def test_project_assessment_combines_user_and_engineering_context(mocker):
    source_code = "FastAPI app includes repository and auth routers."
    mocker.patch.object(
        SearchService,
        "search",
        return_value={
            "documents": [[source_code]],
            "metadatas": [[{"path": "main.py", "start": 10, "end": 10}]],
        },
    )
    prompts = []
    mocker.patch(
        "app.services.project_assessment_service.GeminiClient.generate",
        side_effect=lambda prompt: prompts.append(prompt) or "# Project Assessment",
    )

    result = ProjectAssessmentService.generate(
        SimpleNamespace(id=12, name="CodePilot")
    )

    assert result["assessment"] == "# Project Assessment"
    assert result["sources"] == [
        {
            "file": "main.py",
            "start_line": 10,
            "end_line": 10,
            "snippet": source_code,
        }
    ]
    assert "Product and User Perspective" in prompts[0]
    assert "Software Engineering Perspective" in prompts[0]
    assert "main.py" in prompts[0]
    SearchService.search.assert_called_once_with(
        ProjectAssessmentService.RETRIEVAL_QUESTION,
        12,
        top_k=12,
    )


def test_project_assessment_requires_retrieved_source_evidence(mocker):
    mocker.patch.object(
        SearchService,
        "search",
        return_value={"documents": [[]], "metadatas": [[]]},
    )

    with pytest.raises(ProjectAssessmentError, match="Index the repository"):
        ProjectAssessmentService.generate(SimpleNamespace(id=12, name="CodePilot"))
