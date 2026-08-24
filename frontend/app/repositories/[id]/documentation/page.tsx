import { getRepository, getDocumentation } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import MarkdownViewer from "@/app/components/repository/MarkdownViewer";
import Link from "next/link";

type Props = {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ file?: string }>;
};

export default async function DocumentationPage({
  params,
  searchParams,
}: Props) {
  const { id } = await params;
  const { file } = await searchParams;
  const repoId = Number(id);
  const repo = await getRepository(repoId);

  if (repo.status !== "INDEXED") {
    return (
      <div className="max-w-6xl mx-auto p-8">
        <RepositoryHeader repoId={repoId} repoName={repo.name} title="File Documentation" />
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-6">
          <h2 className="font-semibold text-amber-900">Index this repository first</h2>
          <p className="mt-2 text-sm leading-6 text-amber-800">Documentation uses the repository index to understand code in context. Start indexing from the repository overview, then return here.</p>
          <Link href={`/repositories/${id}`} className="mt-4 inline-flex rounded-lg bg-amber-900 px-3 py-2 text-sm font-semibold text-white hover:bg-amber-950">Back to repository</Link>
        </div>
      </div>
    );
  }

  if (!file) {
    return (
      <div className="max-w-6xl mx-auto p-8">
        <RepositoryHeader
          repoId={repoId}
          repoName={repo.name}
          title="File Documentation"
        />
        <p className="text-gray-600">
          No file selected.{" "}
          <Link href={`/repositories/${id}/files`} className="text-blue-600 hover:underline">
            Browse files
          </Link>{" "}
          and click Documentation on a file.
        </p>
      </div>
    );
  }

  const result = await getDocumentation(repoId, file);

  return (
    <div className="max-w-6xl mx-auto p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="File Documentation"
        subtitle={file}
      />
      <MarkdownViewer content={result.documentation} />
    </div>
  );
}
