import MainLayout from "../components/layout/MainLayout";
import RepositoryActionLauncher from "../components/repository/RepositoryActionLauncher";

export default function AnalysisPage() {
  return (
    <MainLayout>
      <RepositoryActionLauncher title="Analysis" description="Run maintainability, dependency, and health checks on any indexed repository." actions={[
        { label: "Complexity analysis", href: "/repositories/:id/complexity", description: "Find complex files, code smells, and technical debt." },
        { label: "Dependency analysis", href: "/repositories/:id/dependency-analysis", description: "Inspect coupling, circular imports, and recommendations." },
        { label: "Health score", href: "/repositories/:id/health", description: "Get a consolidated codebase health report." },
        { label: "Production readiness", href: "/repositories/:id/production", description: "Assess deployment and operational readiness." },
      ]} />
    </MainLayout>
  );
}
