from app.services.repository_diagram_service import RepositoryDiagramService


class SequenceDiagramService:
    @staticmethod
    def generate(repository) -> dict:
        return RepositoryDiagramService.generate(
            repository,
            "sequence diagram",
            "Find application entry points, request handling, service calls, data "
            "access, and external API interactions. Prefer request and response flow.",
            "sequenceDiagram",
        )
