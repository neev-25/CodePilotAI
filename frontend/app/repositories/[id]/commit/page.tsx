import { getRepository } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import CommitForm from "@/app/components/repository/forms/CommitForm";

type Props = { params: Promise<{ id: string }> };

export default async function CommitPage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);
  const repo = await getRepository(repoId);

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-8 h-[calc(100vh-6rem)] flex flex-col">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="Commit Message Builder"
        subtitle="Standardize commit logs analyzing raw snippet abstractions."
      />
      <div className="mt-6 flex-1 bg-gray-50 rounded-xl border border-[var(--border)] shadow-sm overflow-y-auto">
        <CommitForm repoId={repoId} />
      </div>
    </div>
  );
}
