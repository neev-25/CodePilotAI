import { getRepository, getReadme } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import MarkdownViewer from "@/app/components/repository/MarkdownViewer";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function ReadmePage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);
  const repo = await getRepository(repoId);
  const data = await getReadme(repoId);

  return (
    <div className="max-w-6xl mx-auto p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="README Generator"
      />
      <MarkdownViewer content={data.readme} />
    </div>
  );
}
