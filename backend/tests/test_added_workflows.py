from types import SimpleNamespace

import pytest

from app.services.production_readiness_service import (
    ProductionReadinessError,
    ProductionReadinessService,
)
from app.services.repository_diagram_service import (
    DiagramGenerationError,
    RepositoryDiagramService,
)
from app.services.search_service import SearchService
from app.services.test_generator_service import (
    InvalidTestSourceError,
    TestGeneratorService,
)
from app.models.repository import Repository
from main import app


def test_repository_diagram_is_generated_from_retrieved_source(mocker):
    source = "router.get('/items', list_items)"
    mocker.patch.object(
        SearchService,
        "search",
        return_value={
            "documents": [[source]],
            "metadatas": [[{"path": "api.py", "start": 8, "end": 8}]],
        },
    )
    mocker.patch(
        "app.services.repository_diagram_service.GeminiClient.generate",
        return_value="flowchart TD\n  API --> Items",
    )

    result = RepositoryDiagramService.generate(
        SimpleNamespace(id=4, name="Sample"),
        "flowchart",
        "Find application flow",
        "flowchart",
    )

    assert result["mermaid"] == "flowchart TD\n  API --> Items"
    assert result["sources"][0]["file"] == "api.py"


def test_repository_diagram_rejects_empty_or_wrong_diagram_output(mocker):
    mocker.patch.object(
        SearchService,
        "search",
        return_value={"documents": [["source"]], "metadatas": [[{"path": "main.py"}]]},
    )
    mocker.patch(
        "app.services.repository_diagram_service.GeminiClient.generate",
        return_value="classDiagram\n  class App",
    )

    with pytest.raises(DiagramGenerationError, match="invalid flowchart"):
        RepositoryDiagramService.generate(
            SimpleNamespace(id=4, name="Sample"),
            "flowchart",
            "Find application flow",
            "flowchart",
        )


def test_test_generator_uses_real_source_and_returns_framework_tests(
    mocker,
    tmp_path,
):
    source = tmp_path / "src" / "math_utils.py"
    source.parent.mkdir()
    source.write_text(
        "def add(left, right):\n    return left + right\n",
        encoding="utf-8",
    )
    generated = {
        "source_file": "src/math_utils.py",
        "test_file_path": "tests/test_math_utils.py",
        "framework": "unittest",
        "summary": "Covers addition behavior.",
        "test_cases": [
            {
                "name": "adds integers",
                "category": "happy path",
                "purpose": "Checks integer addition.",
                "expected_result": "The values are summed.",
            }
        ],
        "test_code": (
            "import unittest\nfrom src.math_utils import add\n\n"
            "class AddTests(unittest.TestCase):\n"
            "    def test_adds_integers(self):\n"
            "        self.assertEqual(add(2, 3), 5)\n"
        ),
    }
    generate_json = mocker.patch(
        "app.services.test_generator_service.GeminiClient.generate_json",
        return_value=generated,
    )

    result = TestGeneratorService.generate(
        SimpleNamespace(local_path=str(tmp_path), name="Sample"),
        "src/math_utils.py",
    )

    assert result == generated
    prompt = generate_json.call_args.args[0]
    assert "def add(left, right)" in prompt
    assert "unittest" in prompt


def test_test_generator_rejects_paths_that_escape_repository(tmp_path):
    with pytest.raises(InvalidTestSourceError, match="inside this repository"):
        TestGeneratorService._resolve_source(
            SimpleNamespace(local_path=str(tmp_path)),
            "../outside.py",
        )


def test_test_generator_detects_framework_in_nested_project_manifest(tmp_path):
    source = tmp_path / "frontend" / "src" / "component.tsx"
    source.parent.mkdir(parents=True)
    source.write_text("export function Component() { return null; }", encoding="utf-8")
    (tmp_path / "frontend" / "package.json").write_text(
        '{"devDependencies":{"vitest":"^2.0.0"}}',
        encoding="utf-8",
    )

    framework, test_path = TestGeneratorService._select_framework(tmp_path, source)

    assert framework == "vitest"
    assert test_path == "component.test.tsx"


def test_production_readiness_uses_detected_file_evidence_and_validates_model(
    mocker,
    tmp_path,
):
    (tmp_path / "README.md").write_text("# Sample", encoding="utf-8")
    (tmp_path / "Dockerfile").write_text("FROM python:3.12", encoding="utf-8")
    (tmp_path / ".env.example").write_text("API_KEY=", encoding="utf-8")
    (tmp_path / ".env").write_text("SECRET_VALUE=must-not-be-read", encoding="utf-8")
    (tmp_path / "main.py").write_text(
        '@app.get("/health")\ndef health(): return {"status": "ok"}',
        encoding="utf-8",
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_app.py").write_text(
        "def test_example(): pass",
        encoding="utf-8",
    )
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text(
        "name: CI",
        encoding="utf-8",
    )
    mock_llm = mocker.patch(
        "app.services.production_readiness_service.GeminiClient.generate_json",
        return_value={
            "production_score": 70,
            "readiness": "Ready with risks",
            "summary": "Some release work remains.",
            "scalability": "No load tests found.",
            "maintainability": "The project has a README.",
            "security": "Review secret management.",
            "testing": "Test files exist, execution not verified.",
            "observability": "No health check found.",
            "deployment": "Container configuration exists.",
            "risks": ["Operations are not validated."],
            "blockers": [],
            "recommendations": ["Run CI before release."],
            "go_live": True,
        },
    )

    report = ProductionReadinessService.analyze(
        SimpleNamespace(local_path=str(tmp_path), name="Sample")
    )

    evidence = {item["area"]: item for item in report["evidence"]}
    assert evidence["Automated tests"]["status"] == "present"
    assert evidence["Continuous integration"]["status"] == "present"
    assert evidence["Deployment configuration"]["status"] == "present"
    assert evidence["Safe environment configuration"]["status"] == "present"
    assert evidence["Operational health checks"]["status"] == "present"
    assert report["go_live"] is False
    assert "must-not-be-read" not in mock_llm.call_args.args[0]


def test_production_readiness_reports_invalid_ai_output(mocker, tmp_path):
    mocker.patch(
        "app.services.production_readiness_service.GeminiClient.generate_json",
        return_value={"production_score": "unknown"},
    )

    with pytest.raises(ProductionReadinessError, match="required report format"):
        ProductionReadinessService.analyze(
            SimpleNamespace(local_path=str(tmp_path), name="Sample")
        )


def test_five_requested_workflows_are_registered_as_repository_routes():
    paths = app.openapi()["paths"]

    assert "/repositories/{repository_id}/sequence-diagram" in paths
    assert "/repositories/{repository_id}/class-diagram" in paths
    assert "/repositories/{repository_id}/flowchart" in paths
    assert "/repositories/{repository_id}/production-readiness" in paths
    assert "/repositories/{repository_id}/test-cases" in paths


def test_test_case_api_requires_indexed_owned_repository_and_returns_report(
    client,
    auth_headers,
    db_session,
    mocker,
):
    mocker.patch(
        "app.api.repository.GitService.clone",
        return_value=("sample", "C:/repositories/sample"),
    )
    created = client.post(
        "/repositories",
        json={"github_url": "https://github.com/example/sample"},
        headers=auth_headers,
    )
    assert created.status_code in (200, 201)
    repository_id = created.json()["id"]
    repository = db_session.query(Repository).filter_by(id=repository_id).one()
    repository.status = "INDEXED"
    db_session.commit()

    generated = {
        "source_file": "src/math_utils.py",
        "test_file_path": "tests/test_math_utils.py",
        "framework": "unittest",
        "summary": "Covers integer addition.",
        "test_cases": [
            {
                "name": "adds integers",
                "category": "happy path",
                "purpose": "Checks the sum.",
                "expected_result": "Returns the sum.",
            }
        ],
        "test_code": (
            "import unittest\n"
            "class AddTests(unittest.TestCase):\n"
            "    def test_add(self): self.assertEqual(2 + 3, 5)\n"
        ),
    }

    def generate_directly(_db, _repository, _artifact, generate, inputs=None):
        return generate()

    mocker.patch(
        "app.api.repository.cached_analysis",
        side_effect=generate_directly,
    )
    generator = mocker.patch.object(
        TestGeneratorService,
        "generate",
        return_value=generated,
    )

    response = client.post(
        f"/repositories/{repository_id}/test-cases",
        json={"file_path": "src/math_utils.py"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["test_file_path"] == "tests/test_math_utils.py"
    generator.assert_called_once_with(repository, "src/math_utils.py")
