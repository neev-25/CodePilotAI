from collections import Counter

from app.ai.chunker import CodeChunker
from app.ai.reader import FileReader
from app.ai.scanner import RepositoryScanner
from app.ai.vector_store import VectorStore
from pathlib import Path

EXTENSION_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".jsx": "JavaScript",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
    ".md": "Markdown",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".html": "HTML",
    ".css": "CSS",
    ".sql": "SQL",
}


class RepositoryStatsService:

    @staticmethod
    def get_stats(repository):

        files = RepositoryScanner.scan(
            repository.local_path
        )

        documents = FileReader.read_many(files)

        chunks = CodeChunker.chunk_many(documents)

        vector_store = VectorStore()

        vector_count = vector_store.repository_count(
            repository.id
        )

        language_counter = Counter()

        for file in files:

            suffix = Path(file).suffix.lower()
        
            language = EXTENSION_MAP.get(
                suffix,
                "Other",
            )
        
            language_counter[language] += 1

        return {
            "repository": repository.name,
            "status": repository.status,
            "files": len(files),
            "documents": len(documents),
            "chunks": len(chunks),
            "vectors": vector_count,
            "languages": dict(language_counter),
        }