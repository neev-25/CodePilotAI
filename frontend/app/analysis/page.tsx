import MainLayout from "../components/layout/MainLayout";
import RepositoryActionLauncher from "../components/repository/RepositoryActionLauncher";

export default function AnalysisPage() {
  return (
    <MainLayout>
      <RepositoryActionLauncher title="Project Analysis" description="Understand user value and engineering quality with evidence from an indexed repository." actions={[
        { label: "Project assessment", href: "/repositories/:id/assessment", description: "Review product/user value and software-engineering characteristics with citations." },
        { label: "Engineering health", href: "/repositories/:id/health", description: "See maintainability, security, architecture, and complexity scores with prioritized actions." },
        { label: "Security analysis", href: "/repositories/:id/security", description: "Inspect security, reliability, and bug findings." },
        { label: "Developer onboarding", href: "/repositories/:id/onboarding", description: "Generate an evidence-based guide for understanding the codebase." },
      ]} />
    </MainLayout>
  );
}
