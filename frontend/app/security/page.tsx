import MainLayout from "../components/layout/MainLayout";
import RepositoryActionLauncher from "../components/repository/RepositoryActionLauncher";

export default function SecurityGlobalPage() {
  return (
    <MainLayout>
      <RepositoryActionLauncher title="Security" description="Find vulnerabilities, reliability problems, and security risks." actions={[
        { label: "Security analysis", href: "/repositories/:id/security", description: "Review bugs, security findings, and reliability issues." },
        { label: "Repository review", href: "/repositories/:id/review", description: "Get an overall quality review and prioritized recommendations." },
      ]} />
    </MainLayout>
  );
}
