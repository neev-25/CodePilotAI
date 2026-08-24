import { getRepository, getRepositoryTree } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import FileTreeList from "@/app/components/repository/FileTreeList";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function FilesPage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);

  const [repo, treeData] = await Promise.all([
    getRepository(repoId),
    getRepositoryTree(repoId),
  ]);

  return (
    <div className="max-w-6xl mx-auto p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="File Explorer"
        subtitle={`Browse files in ${treeData.repository}`}
      />
      <FileTreeList repoId={id} nodes={treeData.tree} />
    </div>
  );
}
