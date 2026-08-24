import hashlib
import json
from pathlib import Path
from typing import Dict, List

from app.core.config import settings


class FileHashService:
    """
    Maintains a per-repository SHA-256 hash ledger so that re-indexing
    only embeds new or modified files.
    """

    @staticmethod
    def _ledger_path(repository_id: int) -> Path:
        settings.VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
        return settings.VECTOR_STORE_PATH / f"{repository_id}_hashes.json"

    @staticmethod
    def load(repository_id: int) -> Dict[str, str]:
        """Return {file_path: sha256} from the stored ledger (empty dict if absent)."""
        ledger = FileHashService._ledger_path(repository_id)
        if not ledger.exists():
            return {}
        try:
            return json.loads(ledger.read_text(encoding="utf-8"))
        except Exception:
            return {}

    @staticmethod
    def save(repository_id: int, hashes: Dict[str, str]) -> None:
        """Persist the updated hash ledger."""
        FileHashService._ledger_path(repository_id).write_text(
            json.dumps(hashes, indent=2), encoding="utf-8"
        )

    @staticmethod
    def hash_content(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def changed_documents(
        documents: List[Dict],
        stored: Dict[str, str],
    ) -> tuple[List[Dict], Dict[str, str]]:
        """
        Filter `documents` to only those that are new or changed.

        Returns:
            changed   - documents needing re-embedding
            new_hashes - complete updated ledger (unchanged paths kept as-is)
        """
        new_hashes: Dict[str, str] = dict(stored)  # carry over unchanged
        changed: List[Dict] = []

        for doc in documents:
            path = doc.get("path", "")
            content = doc.get("content", "")
            digest = FileHashService.hash_content(content)
            if stored.get(path) != digest:
                changed.append(doc)
            new_hashes[path] = digest

        return changed, new_hashes
