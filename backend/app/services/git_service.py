import hashlib
import re
from pathlib import Path

from git import Repo
from git.exc import GitCommandError
from app.core.config import settings


BASE_DIR = settings.REPOSITORY_ROOT.resolve()
BASE_DIR.mkdir(exist_ok=True)


class GitService:

    @staticmethod
    def clone(url: str):
        url = url.strip()
        if not url:
            raise ValueError("A repository URL is required.")

        repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
        repo_name = re.sub(r"[^A-Za-z0-9._-]", "-", repo_name) or "repository"
        destination = BASE_DIR / f"{repo_name}-{hashlib.sha256(url.encode()).hexdigest()[:10]}"

        # Repository already cloned
        if destination.exists():
            return repo_name, str(destination)

        try:
            Repo.clone_from(url, destination)
        except GitCommandError as error:
            raise ValueError("Unable to clone the repository. Check the URL and repository access.") from error

        return repo_name, str(destination)
