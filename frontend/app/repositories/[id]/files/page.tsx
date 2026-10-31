import { getRepository, getRepositoryTree, getFileContent } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import FileTreeList from "@/app/components/repository/FileTreeList";
import CodeViewer from "@/app/components/repository/CodeViewer";

type Props = {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
};

export default async function FilesPage({ params, searchParams }: Props) {
  const { id } = await params;
  const repoId = Number(id);
  const resolvedSearchParams = await searchParams;
  const selectedFile = typeof resolvedSearchParams.file === "string" ? resolvedSearchParams.file : null;

  const [repo, treeData] = await Promise.all([
    getRepository(repoId),
    getRepositoryTree(repoId),
  ]);

  let fileContent = "";
  if (selectedFile) {
    try {
      const res = await getFileContent(repoId, selectedFile);
      fileContent = res?.content || "";
    } catch {
      fileContent = "Error: File could not be loaded or contains binary data.";
    }
  }

  const ext = selectedFile?.split(".").pop() || "typescript";

  return (
    <div className="max-w-[1400px] mx-auto p-4 md:p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="File Explorer"
        subtitle={`Browse files in ${treeData.repository}`}
      />

      <div className="mt-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-4 max-h-[80vh] overflow-y-auto pr-2 border-r border-[var(--border)]">
          <FileTreeList repoId={id} nodes={treeData.tree} selectedFile={selectedFile} />
        </div>

        <div className="lg:col-span-8 flex flex-col gap-4">
          {selectedFile ? (
            <>
              <div className="flex items-center rounded-xl border border-[var(--border)] bg-white p-4 shadow-sm">
                <div className="font-semibold">{selectedFile}</div>
              </div>
              <CodeViewer code={fileContent} language={ext} />
            </>
          ) : (
            <div className="flex h-64 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface-50)] text-[var(--muted)]">
              Select a file from the explorer to view its contents and run AI actions.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
