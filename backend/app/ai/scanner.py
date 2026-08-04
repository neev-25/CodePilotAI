from pathlib import Path


IGNORE_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "dist",
    "build",
}


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".md",
    ".json",
    ".html",
    ".css",
}


class RepositoryScanner:

    @staticmethod
    def scan(repository_path: str):

        files = []

        root = Path(repository_path)

        for file in root.rglob("*"):

            if not file.is_file():
                continue

            if any(
                ignored in file.parts
                for ignored in IGNORE_DIRS
            ):
                continue

            if file.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            files.append(file)

        return files