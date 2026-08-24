import { getRepository, getDependencyGraph } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import DependencyGraphView from "@/app/components/repository/DependencyGraphView";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function DependencyGraphPage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);
  const repo = await getRepository(repoId);
  const graph = await getDependencyGraph(repoId);

  return (
    <div className="max-w-6xl mx-auto p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="Dependency Graph"
        subtitle={`${graph.nodes.length} modules, ${graph.edges.length} dependencies`}
      />

      <DependencyGraphView graph={graph} />

      {graph.external_dependencies.length > 0 && (
        <div className="mt-8">
          <h2 className="text-xl font-bold mb-4">External Dependencies</h2>
          <div className="flex flex-wrap gap-2">
            {graph.external_dependencies.map((dep) => (
              <span
                key={dep}
                className="px-3 py-1 bg-gray-100 rounded-lg text-sm"
              >
                {dep}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
