import { getRepository } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import TestGeneratorForm from "@/app/components/repository/forms/TestGeneratorForm";

type Props = {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ file?: string }>;
};

export default async function TestsPage({ params, searchParams }: Props) {
  const { id } = await params;
  const { file } = await searchParams;
  const repoId = Number(id);
  const repo = await getRepository(repoId);

  return (
    <div className="max-w-6xl mx-auto p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="Test Generator"
        subtitle={file ?? "Enter a file path to generate tests"}
      />
      <TestGeneratorForm repoId={repoId} filePath={file} />
    </div>
  );
}
