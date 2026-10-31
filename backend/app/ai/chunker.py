from langchain_text_splitters import RecursiveCharacterTextSplitter


class CodeChunker:

    CHUNK_SIZE = 1200
    OVERLAP = 200

    @staticmethod
    def chunk(document: dict):
        path = document["path"]
        content = document["content"]
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CodeChunker.CHUNK_SIZE,
            chunk_overlap=CodeChunker.OVERLAP,
            add_start_index=True,
            strip_whitespace=False,
            separators=["\n\n", "\n", " ", ""],
        )

        chunks = []
        for split_document in splitter.create_documents(
            [content],
            metadatas=[{"path": path}],
        ):
            start_index = split_document.metadata["start_index"]
            start_line = content.count("\n", 0, start_index) + 1
            last_char_index = start_index + max(len(split_document.page_content) - 1, 0)
            chunks.append(
                {
                    "path": path,
                    "start_line": start_line,
                    "end_line": content.count("\n", 0, last_char_index) + 1,
                    "content": split_document.page_content,
                }
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