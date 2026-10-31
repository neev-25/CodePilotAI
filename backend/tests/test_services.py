"""Service-layer unit tests — no real LLM calls, no real filesystem."""

from app.services.file_hash_service import FileHashService
from app.services.analysis_cache_service import AnalysisCacheService


# ── FileHashService ─────────────────────────────────────────────────────────

class TestFileHashService:

    def test_all_files_changed_on_empty_ledger(self):
        docs = [
            {"path": "a.py", "content": "print('hello')"},
            {"path": "b.py", "content": "x = 1"},
        ]
        changed, new_hashes = FileHashService.changed_documents(docs, {})
        assert len(changed) == 2
        assert set(new_hashes.keys()) == {"a.py", "b.py"}

    def test_unchanged_file_is_skipped(self):
        docs = [{"path": "a.py", "content": "print('hello')"}]
        _, hashes = FileHashService.changed_documents(docs, {})

        # Second run — same content
        changed, _ = FileHashService.changed_documents(docs, hashes)
        assert changed == []

    def test_modified_file_is_included(self):
        docs = [{"path": "a.py", "content": "print('hello')"}]
        _, hashes = FileHashService.changed_documents(docs, {})

        docs_v2 = [{"path": "a.py", "content": "print('world')"}]
        changed, _ = FileHashService.changed_documents(docs_v2, hashes)
        assert len(changed) == 1

    def test_new_file_added(self):
        docs_v1 = [{"path": "a.py", "content": "x = 1"}]
        _, hashes = FileHashService.changed_documents(docs_v1, {})

        docs_v2 = [
            {"path": "a.py", "content": "x = 1"},   # unchanged
            {"path": "b.py", "content": "y = 2"},   # new
        ]
        changed, _ = FileHashService.changed_documents(docs_v2, hashes)
        assert len(changed) == 1
        assert changed[0]["path"] == "b.py"

    def test_removed_files_are_removed_from_hash_ledger(self):
        documents = [{"path": "a.py", "content": "unchanged"}]

        changed, new_hashes = FileHashService.changed_documents(
            documents,
            {
                "a.py": FileHashService.hash_content("unchanged"),
                "deleted.py": "deleted-hash",
            },
        )

        assert changed == []
        assert set(new_hashes) == {"a.py"}


# ── AnalysisCacheService ────────────────────────────────────────────────────

class TestAnalysisCacheService:

    def test_cache_miss_calls_generator(self, db_session):
        call_count = {"n": 0}

        def generate():
            call_count["n"] += 1
            return {"result": "analysis_output"}

        result = AnalysisCacheService.get_or_generate(
            db_session, repository_id=1, artifact_type="test_artifact",
            generate=generate,
        )
        assert result == {"result": "analysis_output"}
        assert call_count["n"] == 1

    def test_cache_hit_skips_generator(self, db_session):
        call_count = {"n": 0}

        def generate():
            call_count["n"] += 1
            return {"data": "fresh"}

        # First call — cache miss
        AnalysisCacheService.get_or_generate(
            db_session, repository_id=2, artifact_type="hit_test",
            generate=generate,
        )
        # Second call — should be a cache hit
        AnalysisCacheService.get_or_generate(
            db_session, repository_id=2, artifact_type="hit_test",
            generate=generate,
        )
        assert call_count["n"] == 1  # generator called exactly once

    def test_invalidate_clears_cache(self, db_session):
        call_count = {"n": 0}

        def generate():
            call_count["n"] += 1
            return {"v": call_count["n"]}

        AnalysisCacheService.get_or_generate(
            db_session, repository_id=3, artifact_type="inv_test",
            generate=generate,
        )
        AnalysisCacheService.invalidate_repository(db_session, 3)

        AnalysisCacheService.get_or_generate(
            db_session, repository_id=3, artifact_type="inv_test",
            generate=generate,
        )
        assert call_count["n"] == 2  # generator called again after invalidation
