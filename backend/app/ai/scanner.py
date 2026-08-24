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
    ".go", ".rs", ".rb", ".php", ".cs", ".csproj", ".fs", ".vb",
    ".swift", ".kt", ".kts", ".scala", ".sh", ".bash", ".zsh",
    ".ps1", ".sql", ".r", ".dart", ".vue", ".svelte", ".mjs", ".cjs",
    ".yaml", ".yml", ".toml", ".xml", ".gradle", ".dockerfile",
}

MAX_FILE_BYTES = 1_000_000


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

            # Include extensionless project files (Dockerfile, Makefile, etc.) and
            # common source files from any ecosystem. Binary and huge generated
            # files are excluded by size/content checks in FileReader.
            if file.suffix.lower() not in SUPPORTED_EXTENSIONS and not file.name.lower() in {
                "dockerfile", "makefile", "gemfile", "rakefile", "procfile",
                "license", "readme", "cmakelists.txt",
            }:
                continue

            try:
                if file.stat().st_size > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue

            files.append(file)

        return files
