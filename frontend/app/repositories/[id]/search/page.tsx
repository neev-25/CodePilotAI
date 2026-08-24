import { getRepository } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import SearchForm from "@/app/components/repository/forms/SearchForm";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function SearchPage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);
  const repo = await getRepository(repoId);

  return (
    <div className="max-w-6xl mx-auto p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="Semantic Search"
        subtitle="Ask questions about the repository using RAG"
      />
      <SearchForm repoId={repoId} />
    </div>
  );
}
