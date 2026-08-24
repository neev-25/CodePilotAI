import MainLayout from "../components/layout/MainLayout";
import RepositoryActionLauncher from "../components/repository/RepositoryActionLauncher";

export default function TestingPage() {
  return (
    <MainLayout>
      <RepositoryActionLauncher title="Testing" description="Generate unit tests for a source file in an indexed repository." actions={[
        { label: "Generate tests", href: "/repositories/:id/tests", description: "Choose a file and create a test suite." },
        { label: "Browse source files", href: "/repositories/:id/files", description: "Inspect the file tree before choosing a target." },
      ]} />
    </MainLayout>
  );
}
