from pathlib import Path
from git import Repo


BASE_DIR = Path("repositories")
BASE_DIR.mkdir(exist_ok=True)


class GitService:

    @staticmethod
    def clone(url: str):

        repo_name = url.split("/")[-1].replace(".git", "")

        destination = BASE_DIR / repo_name

        Repo.clone_from(url, destination)

        return repo_name, str(destination)