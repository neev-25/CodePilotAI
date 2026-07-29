from fastapi import HTTPException


class RepositoryAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=409,
            detail="Repository already exists.",
        )


class RepositoryNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="Repository not found.",
        )