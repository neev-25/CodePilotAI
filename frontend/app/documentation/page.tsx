import MainLayout from "../components/layout/MainLayout";
import RepositoryActionLauncher from "../components/repository/RepositoryActionLauncher";

export default function DocumentationGlobalPage() {
  return (
    <MainLayout>
      <RepositoryActionLauncher title="Documentation" description="Generate a README or file-level documentation for an indexed repository." actions={[
        { label: "Generate README", href: "/repositories/:id/readme", description: "Create a project README from the repository source." },
        { label: "Document files", href: "/repositories/:id/documentation", description: "Select a file and generate focused documentation." },
      ]} />
    </MainLayout>
  );
}
