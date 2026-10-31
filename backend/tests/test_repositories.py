"""Repository CRUD endpoint tests."""
import unittest.mock as mock


import pytest
from app.services.git_service import GitService

def _repo_payload(name="my-repo"):
    return {
        "name": name,
        "github_url": f"https://github.com/test/{name}",
        "local_path": f"/tmp/{name}",
    }

@pytest.fixture(autouse=True)
def mock_git_clone(mocker):
    def fake_clone(url):
        # Extract repo name from URL roughly
        name = url.split("/")[-1]
        return name, f"/tmp/{name}"
    mocker.patch.object(GitService, "clone", side_effect=fake_clone)



def test_list_repositories_empty(client, auth_headers):
    resp = client.get("/repositories", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_repository(client, auth_headers):
    resp = client.post("/repositories", json=_repo_payload(), headers=auth_headers)
    assert resp.status_code in (200, 201)
    body = resp.json()
    assert body["name"] == "my-repo"
    assert "id" in body


def test_create_repository_appears_in_list(client, auth_headers):
    client.post("/repositories", json=_repo_payload("listed-repo"), headers=auth_headers)
    resp = client.get("/repositories", headers=auth_headers)
    names = [r["name"] for r in resp.json()]
    assert "listed-repo" in names


def test_get_repository_by_id(client, auth_headers):
    create_resp = client.post("/repositories", json=_repo_payload("get-repo"), headers=auth_headers)
    repo_id = create_resp.json()["id"]

    resp = client.get(f"/repositories/{repo_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == repo_id


def test_delete_repository(client, auth_headers, db_session):
    create_resp = client.post("/repositories", json=_repo_payload("del-repo"), headers=auth_headers)
    repo_id = create_resp.json()["id"]
    from app.models.analysis_cache import AnalysisCache
    from app.models.vector_embedding import VectorEmbedding

    db_session.add(
        AnalysisCache(
            repository_id=repo_id,
            artifact_type="test",
            input_key="{}",
            payload="{}",
        )
    )
    db_session.add(
        VectorEmbedding(
            id=f"repo_{repo_id}_test",
            repository_id=repo_id,
            path="main.py",
            start_line=1,
            end_line=1,
            content="print('test')",
            embedding=[0.0, 0.0, 0.0],
        )
    )
    db_session.commit()

    del_resp = client.delete(f"/repositories/{repo_id}", headers=auth_headers)
    assert del_resp.status_code == 200
    assert db_session.query(AnalysisCache).filter_by(repository_id=repo_id).count() == 0
    assert db_session.query(VectorEmbedding).filter_by(repository_id=repo_id).count() == 0

    get_resp = client.get(f"/repositories/{repo_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_repository_belongs_to_owner(client, auth_headers):
    """Repos created by one user are not visible to another."""
    # Second user
    client.post("/auth/register", json={
        "name": "Other",
        "email": "other@example.com",
        "password": "otherpass99",
    })
    login2 = client.post("/auth/login", json={
        "email": "other@example.com",
        "password": "otherpass99",
    })
    headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}

    # Create repo as user 1
    create_resp = client.post("/repositories", json=_repo_payload("private-repo"), headers=auth_headers)
    repo_id = create_resp.json()["id"]

    # User 2 should NOT see it
    resp = client.get(f"/repositories/{repo_id}", headers=headers2)
    assert resp.status_code == 404


def test_index_repository_reuses_existing_active_job(client, auth_headers, db_session):
    from app.core.constants import RepositoryStatus
    from app.models.indexing_job import IndexingJob
    from app.models.repository import Repository

    create_response = client.post(
        "/repositories",
        json=_repo_payload("already-indexing"),
        headers=auth_headers,
    )
    repository_id = create_response.json()["id"]
    repository = db_session.query(Repository).filter_by(id=repository_id).one()
    repository.status = RepositoryStatus.INDEXING
    active_job = IndexingJob(
        repository_id=repository_id,
        status="RUNNING",
        message="Scanning files.",
    )
    db_session.add(active_job)
    db_session.commit()
    db_session.refresh(active_job)

    response = client.post(
        f"/repositories/{repository_id}/index",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["job_id"] == active_job.id
    assert db_session.query(IndexingJob).filter_by(repository_id=repository_id).count() == 1
