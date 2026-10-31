import hashlib
import re
from pathlib import Path

from git import Repo
from git.exc import GitCommandError
from app.core.config import settings
from app.core.logger import logger


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
        
    @staticmethod
    def get_stats(local_path: str):
        try:
            repo = Repo(local_path)
            head_commit = getattr(repo.head.commit, 'hexsha', None) if repo.head.is_valid() else None
            
            # Simple iteration for stats (can be optimized later for huge repos)
            commits = 0
            contributors = set()
            try:
                for c in repo.iter_commits():
                    commits += 1
                    contributors.add(c.author.email)
            except Exception:
                pass
                
            return {
                "current_commit": head_commit,
                "commits": commits,
                "branches": len(repo.branches),
                "contributors": len(contributors)
            }
        except Exception:
            logger.warning("Could not read git statistics for %s.", local_path, exc_info=True)
            return {
                "current_commit": None,
                "commits": 0,
                "branches": 0,
                "contributors": 0
            }

    @staticmethod
    def get_recent_commits(local_path: str, days: int = 30) -> list[dict]:
        """Fetch the commit history of the repository for the last `days` days."""
        from datetime import datetime, timedelta
        try:
            repo = Repo(local_path)
            cutoff = datetime.now() - timedelta(days=days)
            commits_data = []
            for commit in repo.iter_commits():
                commit_date = datetime.fromtimestamp(commit.committed_date)
                if commit_date < cutoff:
                    break
                commits_data.append({
                    "hash": commit.hexsha[:7],
                    "date": commit_date.strftime("%Y-%m-%d"),
                    "message": commit.message.strip().split('\n')[0],
                    "author": commit.author.name
                })
            return commits_data
        except Exception:
            logger.warning("Could not read recent commits for %s.", local_path, exc_info=True)
            return []
