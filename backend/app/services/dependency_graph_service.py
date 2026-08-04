from pathlib import Path
import re

from app.ai.scanner import RepositoryScanner


class DependencyGraphService:

    IMPORT_PATTERNS = [
        # Python
        r'^\s*from\s+([A-Za-z0-9_\.]+)\s+import',
        r'^\s*import\s+([A-Za-z0-9_\.]+)',

        # ES Modules
        r'^\s*import\s+(?:.+?\s+from\s+)?["\'](.+?)["\']',

        # CommonJS
        r'require\(["\'](.+?)["\']\)',

        # C / C++
        r'^\s*#include\s*[<"](.+?)[>"]',

        # Go
        r'^\s*import\s+"(.+?)"',
    ]

    @staticmethod
    def extract_imports(content: str):

        imports = []

        for line in content.splitlines():

            for pattern in DependencyGraphService.IMPORT_PATTERNS:

                match = re.search(pattern, line)

                if match:
                    imports.append(match.group(1).strip())

        return imports

    @staticmethod
    def resolve_module(
        module: str,
        current_file: Path,
        repository_root: Path,
        file_lookup: dict,
    ):
        """
        Resolve a module import to a repository file if possible.
        Returns the relative repository path or None.
        """

        # -------------------------
        # Relative imports
        # -------------------------

        if module.startswith("."):

            base = (current_file.parent / module)

            candidates = [
                base,
                base.with_suffix(".py"),
                base.with_suffix(".js"),
                base.with_suffix(".ts"),
                base.with_suffix(".jsx"),
                base.with_suffix(".tsx"),
                base / "__init__.py",
                base / "index.js",
                base / "index.ts",
            ]

            for candidate in candidates:

                try:

                    relative = candidate.relative_to(repository_root)

                    relative = relative.as_posix()

                    if relative in file_lookup:
                        return relative

                except Exception:
                    continue

            return None

        # -------------------------
        # Absolute project imports
        # -------------------------

        normalized = module.replace(".", "/")

        for relative in file_lookup:

            without_suffix = str(Path(relative).with_suffix("")).replace("\\", "/")

            if (
                normalized == without_suffix
                or normalized.endswith(without_suffix)
            ):
                return relative

        return None

    @staticmethod
    def build(repository):

        repository_root = Path(repository.local_path).resolve()

        files = RepositoryScanner.scan(repository.local_path)

        nodes = []

        edges = []

        external_dependencies = set()

        file_lookup = {}

        # -------------------------
        # Build lookup
        # -------------------------

        for file in files:

            absolute = Path(file).resolve()

            relative = absolute.relative_to(repository_root).as_posix()

            file_lookup[relative] = absolute

            nodes.append(
                {
                    "path": relative
                }
            )

        # -------------------------
        # Build dependency graph
        # -------------------------

        for file in files:

            absolute = Path(file).resolve()

            relative = absolute.relative_to(repository_root).as_posix()

            try:

                content = absolute.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )

            except Exception:
                continue

            imports = DependencyGraphService.extract_imports(content)

            for module in imports:

                target = DependencyGraphService.resolve_module(
                    module,
                    absolute,
                    repository_root,
                    file_lookup,
                )

                if target:

                    edges.append(
                        {
                            "from_file": relative,
                            "to_file": target,
                        }
                    )

                else:

                    external_dependencies.add(module)

        # Remove duplicate edges

        unique = set()

        dedup_edges = []

        for edge in edges:

            key = (
                edge["from_file"],
                edge["to_file"],
            )

            if key not in unique:

                unique.add(key)

                dedup_edges.append(edge)

        return {
            "repository": repository.name,
            "nodes": nodes,
            "edges": dedup_edges,
            "external_dependencies": sorted(
                external_dependencies
            ),
        }