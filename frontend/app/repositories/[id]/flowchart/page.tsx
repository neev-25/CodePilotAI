import { getRepository, getFlowchart } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import MermaidViewer from "@/app/components/repository/MermaidViewer";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function FlowchartPage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);
  const repo = await getRepository(repoId);
  const data = await getFlowchart(repoId);

  return (
    <div className="max-w-6xl mx-auto p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="Flowchart"
      />
      <MermaidViewer chart={data.mermaid} fallback={data.fallback} />
    </div>
  );
}
