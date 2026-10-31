import MainLayout from "../components/layout/MainLayout";
import RepositoryActionLauncher from "../components/repository/RepositoryActionLauncher";

export default function SearchGlobalPage() {
  return (
    <MainLayout>
      <RepositoryActionLauncher title="Codebase Q&A" description="Ask natural-language questions and get answers grounded in indexed source code." actions={[
        { label: "Open repository chat", href: "/repositories/:id/chat", description: "Get RAG-powered answers with file and line citations." },
      ]} />
    </MainLayout>
  );
}
