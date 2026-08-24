import { getRepository, getClassDiagram } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import MermaidViewer from "@/app/components/repository/MermaidViewer";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function ClassDiagramPage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);
  const repo = await getRepository(repoId);
  const data = await getClassDiagram(repoId);

  return (
    <div className="max-w-6xl mx-auto p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="Class Diagram"
      />
      <MermaidViewer chart={data.mermaid} fallback={data.fallback} />
    </div>
  );
}
