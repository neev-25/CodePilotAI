import MainLayout from "../components/layout/MainLayout";
import RepositoryActionLauncher from "../components/repository/RepositoryActionLauncher";

export default function ArchitectureGlobalPage() {
  return (
    <MainLayout>
      <RepositoryActionLauncher title="Architecture & Dependencies" description="Explore the repository's modules and structural relationships." actions={[
        { label: "Dependency map", href: "/repositories/:id/dependency-graph", description: "Visualize internal modules and their dependencies." },
      ]} />
    </MainLayout>
  );
}
