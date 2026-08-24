import MainLayout from "../components/layout/MainLayout";
import RepositoryActionLauncher from "../components/repository/RepositoryActionLauncher";

export default function SearchGlobalPage() {
  return (
    <MainLayout>
      <RepositoryActionLauncher title="Semantic Search" description="Ask natural-language questions about an indexed codebase." actions={[
        { label: "Open code search", href: "/repositories/:id/search", description: "Search the repository with RAG-powered answers and source citations." },
      ]} />
    </MainLayout>
  );
}
