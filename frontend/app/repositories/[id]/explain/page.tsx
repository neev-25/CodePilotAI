import { getRepository, explainFile } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import MarkdownViewer from "@/app/components/repository/MarkdownViewer";
import ErrorCard from "@/app/components/repository/ErrorCard";
import Link from "next/link";

type Props = {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ file?: string }>;
};

export default async function ExplainFilePage({ params, searchParams }: Props) {
  const { id } = await params;
  const { file } = await searchParams;
  const repoId = Number(id);

  const repo = await getRepository(repoId);

  if (!file) {
    return (
      <div className="max-w-6xl mx-auto p-8">
        <RepositoryHeader repoId={repoId} repoName={repo.name} title="Explain File" />
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

  const result = await explainFile(repoId, file).catch(() => null);

  if (!result) {
    return (
      <ErrorCard
        title="Failed to Explain File"
        message={`Could not generate explanation for ${file}.`}
        backHref={`/repositories/${id}/files`}
      />
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="File Explanation"
        subtitle={file}
      />
      <MarkdownViewer content={result.explanation} />
    </div>
  );
}
