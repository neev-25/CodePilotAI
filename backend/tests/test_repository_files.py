from types import SimpleNamespace


def test_repository_file_content_returns_text_with_safe_relative_path(
    client,
    auth_headers,
    mocker,
    tmp_path,
):
    source = tmp_path / "src" / "main.py"
    source.parent.mkdir()
    source.write_text("print('hello')\n", encoding="utf-8")
    mocker.patch(
        "app.api.repository.RepositoryRepository.get_by_id",
        return_value=SimpleNamespace(local_path=str(tmp_path)),
    )

    response = client.get(
        "/repositories/12/files/content",
        params={"file_path": "src/main.py"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "path": "src/main.py",
        "content": source.read_bytes().decode("utf-8"),
    }


def test_repository_file_content_rejects_paths_outside_repository(
    client,
    auth_headers,
    mocker,
    tmp_path,
):
    mocker.patch(
        "app.api.repository.RepositoryRepository.get_by_id",
        return_value=SimpleNamespace(local_path=str(tmp_path)),
    )

    response = client.get(
        "/repositories/12/files/content",
        params={"file_path": "../outside.txt"},
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid repository file path."


def test_repository_file_content_returns_not_found_for_missing_file(
    client,
    auth_headers,
    mocker,
    tmp_path,
):
    mocker.patch(
        "app.api.repository.RepositoryRepository.get_by_id",
        return_value=SimpleNamespace(local_path=str(tmp_path)),
    )

    response = client.get(
        "/repositories/12/files/content",
        params={"file_path": "missing.py"},
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Repository file not found."


def test_repository_file_content_rejects_binary_files(
    client,
    auth_headers,
    mocker,
    tmp_path,
):
    (tmp_path / "image.bin").write_bytes(b"\x00\xff")
    mocker.patch(
        "app.api.repository.RepositoryRepository.get_by_id",
        return_value=SimpleNamespace(local_path=str(tmp_path)),
    )

    response = client.get(
        "/repositories/12/files/content",
        params={"file_path": "image.bin"},
        headers=auth_headers,
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Binary files cannot be displayed."


def test_repository_file_content_rejects_oversized_files(
    client,
    auth_headers,
    mocker,
    tmp_path,
):
    (tmp_path / "large.txt").write_bytes(b"a" * 1_000_001)
    mocker.patch(
        "app.api.repository.RepositoryRepository.get_by_id",
        return_value=SimpleNamespace(local_path=str(tmp_path)),
    )

    response = client.get(
        "/repositories/12/files/content",
        params={"file_path": "large.txt"},
        headers=auth_headers,
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Repository file is too large to display."
