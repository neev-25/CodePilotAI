import MainLayout from "../components/layout/MainLayout";
import RepositoryActionLauncher from "../components/repository/RepositoryActionLauncher";

export default function ArchitectureGlobalPage() {
  return (
    <MainLayout>
      <RepositoryActionLauncher title="Architecture" description="Generate architecture explanations and diagrams for an indexed repository." actions={[
        { label: "Architecture report", href: "/repositories/:id/architecture", description: "Generate a high-level system architecture explanation." },
        { label: "Dependency graph", href: "/repositories/:id/dependency-graph", description: "Visualize module relationships." },
        { label: "Sequence diagram", href: "/repositories/:id/sequence", description: "Generate an interaction sequence diagram." },
        { label: "Class diagram", href: "/repositories/:id/class-diagram", description: "Generate a class-level diagram." },
        { label: "Flowchart", href: "/repositories/:id/flowchart", description: "Generate a repository flowchart." },
      ]} />
    </MainLayout>
  );
}
