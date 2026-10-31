import ErrorCard from "@/app/components/repository/ErrorCard";
import ReportLayout from "@/app/components/repository/ReportLayout";
import TestGeneratorPanel from "@/app/components/repository/reports/TestGeneratorPanel";
import {
  getRepository,
  getRepositoryTree,
  type FileTreeNode,
} from "@/app/lib/repository";

type Props = {
  params: Promise<{ id: string }>;
};

const SOURCE_EXTENSIONS = new Set([
  "py",
  "js",
  "jsx",
  "ts",
  "tsx",
  "go",
  "rs",
  "java",
]);

function collectSourceFiles(nodes: FileTreeNode[], prefix = ""): string[] {
  return nodes.flatMap((node) => {
    const path = prefix ? `${prefix}/${node.name}` : node.name;
    if (node.type === "directory") {
      return collectSourceFiles(node.children ?? [], path);
    }
    return SOURCE_EXTENSIONS.has(path.split(".").pop()?.toLowerCase() ?? "")
      ? [path]
      : [];
  });
}

export default async function TestGeneratorPage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);
  const [repository, tree] = await Promise.all([
    getRepository(repoId),
    getRepositoryTree(repoId),
  ]);
  const sourceFiles = collectSourceFiles(tree.tree).sort();

  return (
    <ReportLayout
      repoId={repoId}
      repoName={repository.name}
      title="Test Case Generator"
      subtitle="Generate runnable, framework-aware tests from a real source file."
      filename={`${repository.name}-test-generation.pdf`}
      showExport={false}
    >
      {sourceFiles.length > 0 ? (
        <TestGeneratorPanel
          repoId={repoId}
          repoName={repository.name}
          sourceFiles={sourceFiles}
        />
      ) : (
        <ErrorCard
          title="No supported source files were found in this repository."
          backHref={`/repositories/${repoId}`}
        />
      )}
    </ReportLayout>
  );
}
