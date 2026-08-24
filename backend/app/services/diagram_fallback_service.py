"""Useful local Mermaid diagrams when the remote AI provider is unavailable."""

from pathlib import Path
from app.ai.scanner import RepositoryScanner


class DiagramFallbackService:
    @staticmethod
    def _paths(repository, limit: int = 8) -> list[str]:
        root = Path(repository.local_path)
        paths = []
        for file in RepositoryScanner.scan(repository.local_path):
            try:
                paths.append(file.relative_to(root).as_posix())
            except ValueError:
                continue
            if len(paths) == limit:
                break
        return paths or ["repository source"]

    @staticmethod
    def _label(value: str) -> str:
        return value.replace('"', "'")

    @classmethod
    def flowchart(cls, repository) -> dict[str, str]:
        paths = cls._paths(repository)
        lines = ["flowchart TD", '  Start([Developer request]) --> Repo["Repository workspace"]']
        previous = "Repo"
        for index, path in enumerate(paths):
            node = f"File{index}"
            lines.append(f'  {previous} --> {node}["{cls._label(path)}"]')
            previous = node
        lines.append(f"  {previous} --> Result([Analysis result])")
        return {"mermaid": "\n".join(lines), "fallback": True}

    @classmethod
    def sequence(cls, repository) -> dict[str, str]:
        paths = cls._paths(repository, 4)
        first = cls._label(paths[0])
        lines = [
            "sequenceDiagram",
            "  participant User",
            "  participant App as Application",
            f"  participant Source as {first}",
            "  participant Store as Repository data",
            "  User->>App: Request analysis",
            "  App->>Source: Read relevant source",
            "  Source-->>App: Code context",
            "  App->>Store: Retrieve or save result",
            "  Store-->>App: Analysis data",
            "  App-->>User: Display result",
        ]
        return {"mermaid": "\n".join(lines), "fallback": True}

    @classmethod
    def class_diagram(cls, repository) -> dict[str, str]:
        paths = cls._paths(repository)
        lines = ["classDiagram"]
        nodes = []
        for index, path in enumerate(paths):
            node = f"Module{index}"
            nodes.append(node)
            lines.extend([f"  class {node} {{", f'    <<{cls._label(Path(path).stem[:30] or "module")}>>', "  }"])
        for left, right in zip(nodes, nodes[1:]):
            lines.append(f"  {left} --> {right} : source flow")
        return {"mermaid": "\n".join(lines), "fallback": True}
