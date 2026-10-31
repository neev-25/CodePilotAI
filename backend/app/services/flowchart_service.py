from app.services.repository_diagram_service import RepositoryDiagramService


class FlowchartService:
    @staticmethod
    def generate(repository) -> dict:
        return RepositoryDiagramService.generate(
            repository,
            "flowchart",
            "Find the main application entry points and trace the verified "
            "execution flow through routes, services, persistence, and outputs.",
            "flowchart",
        )
