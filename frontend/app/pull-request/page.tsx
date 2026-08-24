import MainLayout from "../components/layout/MainLayout";
import RepositoryActionLauncher from "../components/repository/RepositoryActionLauncher";

export default function PullRequestPage() {
  return (
    <MainLayout>
      <RepositoryActionLauncher title="Pull Requests" description="Draft clear pull-request descriptions for an indexed repository." actions={[
        { label: "Create PR description", href: "/repositories/:id/pr", description: "Generate PR notes from a title and change summary." },
        { label: "Create commit message", href: "/repositories/:id/commit", description: "Generate a concise conventional commit message." },
        { label: "Create changelog", href: "/repositories/:id/changelog", description: "Generate release notes for a version." },
      ]} />
    </MainLayout>
  );
}
