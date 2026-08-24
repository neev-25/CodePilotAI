from pathlib import Path


class FileReader:

    @staticmethod
    def read(file_path: str):

        path = Path(file_path)

        try:
            raw = path.read_bytes()
            if b"\x00" in raw:
                return None
            content = raw.decode("utf-8", errors="replace")

            return {
                "path": str(path),
                "content": content,
            }

        except Exception as e:

            print(f"Error reading {path}: {e}")

            return None

    @staticmethod
    def read_many(files):

        documents = []

        for file in files:

            document = FileReader.read(file)

            if document:

                documents.append(document)

        return documents
