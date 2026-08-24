import { getRepository } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import FunctionExplainForm from "@/app/components/repository/forms/FunctionExplainForm";
import Link from "next/link";

type Props = {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ file?: string }>;
};

export default async function FunctionExplainPage({ params, searchParams }: Props) {
  const { id } = await params;
  const { file } = await searchParams;
  const repoId = Number(id);
  const repo = await getRepository(repoId);

  if (!file) {
    return (
      <div className="max-w-6xl mx-auto p-8">
        <RepositoryHeader repoId={repoId} repoName={repo.name} title="Explain Function" />
        <p className="text-gray-600">
          No file selected.{" "}
          <Link href={`/repositories/${id}/files`} className="text-blue-600 hover:underline">
            Browse files
          </Link>{" "}
          to select one.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="Explain Function"
        subtitle={file}
      />
      <FunctionExplainForm repoId={repoId} filePath={file} />
    </div>
  );
}
