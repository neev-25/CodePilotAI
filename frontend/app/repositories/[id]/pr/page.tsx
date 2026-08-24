import { getRepository } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import PRDescriptionForm from "@/app/components/repository/forms/PRDescriptionForm";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function PRPage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);
  const repo = await getRepository(repoId);

  return (
    <div className="max-w-6xl mx-auto p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="PR Description Generator"
      />
      <PRDescriptionForm repoId={repoId} />
    </div>
  );
}
