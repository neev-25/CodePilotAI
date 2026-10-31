from app.services.repository_diagram_service import RepositoryDiagramService


class ClassDiagramService:
    @staticmethod
    def generate(repository) -> dict:
        return RepositoryDiagramService.generate(
            repository,
            "class diagram",
            "Find the important classes, schemas, models, services, interfaces, "
            "and their relationships or dependencies.",
            "classDiagram",
        )
