from typing import List


class CodeChunker:

    CHUNK_SIZE = 120
    OVERLAP = 20

    @staticmethod
    def chunk(document: dict):

        path = document["path"]
        content = document["content"]

        lines = content.splitlines()

        chunks = []

        start = 0

        while start < len(lines):

            end = min(
                start + CodeChunker.CHUNK_SIZE,
                len(lines),
            )

            chunk = "\n".join(lines[start:end])

            chunks.append(
                {
                    "path": path,
                    "start_line": start + 1,
                    "end_line": end,
                    "content": chunk,
                }
            )

            start += (
                CodeChunker.CHUNK_SIZE
                - CodeChunker.OVERLAP
            )

        return chunks

    @staticmethod
    def chunk_many(documents):

        all_chunks = []

        for document in documents:

            all_chunks.extend(
                CodeChunker.chunk(document)
            )

        return all_chunks