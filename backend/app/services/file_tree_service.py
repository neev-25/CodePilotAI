from pathlib import Path


class FileTreeService:

    IGNORE_DIRS = {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "node_modules",
        ".idea",
        ".vscode",
        "dist",
        "build",
    }

    @staticmethod
    def build_tree(path: Path):

        nodes = []

        for item in sorted(
            path.iterdir(),
            key=lambda x: (
                x.is_file(),
                x.name.lower(),
            ),
        ):

            if item.name in FileTreeService.IGNORE_DIRS:
                continue

            if item.is_dir():

                nodes.append(
                    {
                        "name": item.name,
                        "type": "directory",
                        "children": FileTreeService.build_tree(
                            item
                        ),
                    }
                )

            else:

                nodes.append(
                    {
                        "name": item.name,
                        "type": "file",
                    }
                )

        return nodes

    @staticmethod
    def get_tree(repository):

        root = Path(repository.local_path)

        return {
            "repository": repository.name,
            "tree": FileTreeService.build_tree(root),
        }