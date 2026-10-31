from pathlib import Path
import re

from pydantic import ValidationError

from app.ai.llm import GeminiClient
from app.ai.scanner import RepositoryScanner
from app.schemas.production_readiness import ProductionReadinessResponse


class ProductionReadinessError(ValueError):
    """Raised when the readiness assessment is invalid or lacks repository evidence."""


class ProductionReadinessService:
    @staticmethod
    def _inventory(repository) -> tuple[list[dict], str]:
        root = Path(repository.local_path).resolve()
        paths = {
            file.relative_to(root).as_posix()
            for file in RepositoryScanner.scan(str(root))
        }
        for pattern in (
            "Dockerfile*",
            "docker-compose.y*",
            "compose.y*",
            ".gitlab-ci*",
            ".github/workflows/*",
        ):
            paths.update(
                file.relative_to(root).as_posix()
                for file in root.glob(pattern)
                if file.is_file()
            )
        paths.update(
            file.name
            for file in root.glob(".env*")
            if file.is_file()
            and file.name.lower()
            in {".env.example", ".env.sample", ".env.template"}
        )
        relative_paths = sorted(paths)
        operational_paths = []
        health_check_pattern = re.compile(
            r"\bhealth[\w-]*\b|/health\b|health_check", re.IGNORECASE
        )
        for path in relative_paths:
            source = root / path
            name = source.name.lower()
            if name in {"health.py", "health.ts", "health.js", "healthcheck"}:
                operational_paths.append(path)
                continue
            if (
                source.suffix.lower() not in {".py", ".js", ".jsx", ".ts", ".tsx", ".go"}
                or name not in {"main.py", "app.py", "server.py", "main.ts", "app.ts", "server.ts", "main.js", "app.js", "server.js"}
                or source.stat().st_size > 100_000
            ):
                continue
            if health_check_pattern.search(
                source.read_text(encoding="utf-8", errors="replace")
            ):
                operational_paths.append(path)

        def find_files(area: str) -> list[str]:
            matched = []
            for path in relative_paths:
                normalized = path.lower()
                name = Path(path).name.lower()
                parts = {part.lower() for part in Path(path).parts}
                if area == "Automated tests":
                    found = (
                        bool(parts & {"test", "tests", "spec", "specs"})
                        or name.startswith(("test_", "spec_"))
                        or name.endswith((".test.py", ".spec.py", ".test.js", ".test.ts", ".spec.js", ".spec.ts"))
                    )
                elif area == "Continuous integration":
                    found = normalized.startswith((".github/workflows/", ".gitlab-ci")) or name in {
                        "azure-pipelines.yml",
                        "jenkinsfile",
                        "bitbucket-pipelines.yml",
                    }
                elif area == "Deployment configuration":
                    found = name.startswith("dockerfile") or name in {
                        "docker-compose.yml",
                        "docker-compose.yaml",
                        "compose.yml",
                        "compose.yaml",
                    }
                elif area == "Safe environment configuration":
                    found = name in {".env.example", ".env.sample", ".env.template"}
                elif area == "Project documentation":
                    found = name.startswith("readme")
                else:
                    found = path in operational_paths
                if found:
                    matched.append(path)
            return matched[:10]

        checks = [
            (
                "Automated tests",
                bool(find_files("Automated tests")),
                "Test-related files were found; this review does not execute them.",
            ),
            (
                "Continuous integration",
                bool(find_files("Continuous integration")),
                "CI configuration files were detected.",
            ),
            (
                "Deployment configuration",
                bool(find_files("Deployment configuration")),
                "Container or compose configuration files were detected.",
            ),
            (
                "Safe environment configuration",
                bool(find_files("Safe environment configuration")),
                "A sample environment file was detected; secret values are not inspected.",
            ),
            (
                "Operational health checks",
                bool(find_files("Operational health checks")),
                "Health-check endpoint patterns or files were detected; behavior was not executed.",
            ),
            (
                "Project documentation",
                bool(find_files("Project documentation")),
                "A README file was detected.",
            ),
        ]
        evidence = [
            {
                "area": area,
                "status": "present" if found else "missing",
                "detail": detail
                if found
                else f"No {area.lower()} evidence was found in the repository files.",
                "files": find_files(area),
            }
            for area, found, detail in checks
        ]

        manifest_paths = [
            path
            for path in relative_paths
            if Path(path).name.lower()
            in {
                "pyproject.toml",
                "requirements.txt",
                "package.json",
                "dockerfile",
                "docker-compose.yml",
                "docker-compose.yaml",
                "compose.yml",
                "compose.yaml",
            }
            or path.lower().startswith(".github/workflows/")
        ][:30]
        context = "\n".join(
            [f"File inventory ({len(relative_paths)} files):"]
            + [f"- {path}" for path in relative_paths[:100]]
            + ["\nDeployment, dependency, and CI evidence:"]
            + [f"- {path}" for path in manifest_paths]
        )
        return evidence, context

    @classmethod
    def analyze(cls, repository, health: dict | None = None) -> dict:
        evidence, inventory = cls._inventory(repository)
        prompt = f"""Assess this repository's production readiness using only
the repository inventory, engineering-health summary, and evidence below. Do not claim tests were run or
configurations work: the files have only been inspected. Distinguish detected
files from verified behavior. Be specific, conservative, and actionable.
Return only JSON matching this schema:
{{
  "production_score": 0,
  "readiness": "Not ready | Ready with risks | Production ready",
  "summary": "Concise overall judgment",
  "scalability": "Evidence-based assessment",
  "maintainability": "Evidence-based assessment",
  "security": "Evidence-based assessment",
  "testing": "Evidence-based assessment",
  "observability": "Evidence-based assessment",
  "deployment": "Evidence-based assessment",
  "risks": ["Concrete risk"],
  "blockers": ["Release blocker, if present"],
  "recommendations": ["Prioritized action"],
  "go_live": false
}}
The score must be an integer from 0 to 100. Only set go_live true when the
evidence supports release readiness and blockers is empty.

Repository: {repository.name}
Deterministic evidence inventory: {evidence}
Existing engineering-health analysis (AI-generated; not a substitute for executed checks):
{health or "No engineering-health summary was supplied."}

Inspected repository file inventory:
{inventory}"""
        try:
            generated = GeminiClient().generate_json(prompt)
            if not isinstance(generated, dict):
                raise TypeError("Production-readiness output must be a JSON object.")
            response = ProductionReadinessResponse.model_validate(
                generated | {"evidence": evidence}
            )
        except (TypeError, ValidationError) as error:
            raise ProductionReadinessError(
                "The production-readiness response did not match the required report format."
            ) from error
        if response.blockers or response.production_score < 80:
            response.go_live = False
        return response.model_dump()
