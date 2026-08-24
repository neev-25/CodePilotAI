import { getRepository } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import ChangelogForm from "@/app/components/repository/forms/ChangelogForm";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function ChangelogPage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);
  const repo = await getRepository(repoId);

  return (
    <div className="max-w-6xl mx-auto p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="Changelog Generator"
      />
      <ChangelogForm repoId={repoId} />
    </div>
  );
}
