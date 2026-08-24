import { getRepository, getArchitecture } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import MarkdownViewer from "@/app/components/repository/MarkdownViewer";
import ErrorCard from "@/app/components/repository/ErrorCard";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function ArchitecturePage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);
  const repo = await getRepository(repoId);

  const data = await getArchitecture(repoId).catch(() => null);

  if (!data) {
    return (
      <ErrorCard
        title="Failed to Analyze Architecture"
        backHref={`/repositories/${id}`}
      />
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="Architecture Analysis"
      />
      <MarkdownViewer content={data.architecture} />
    </div>
  );
}
