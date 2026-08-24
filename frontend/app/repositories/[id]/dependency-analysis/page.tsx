import { getRepository, getDependencyAnalysis } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import MarkdownViewer from "@/app/components/repository/MarkdownViewer";
import StatCard from "@/app/components/repository/StatCard";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function DependencyAnalysisPage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);
  const repo = await getRepository(repoId);
  const data = await getDependencyAnalysis(repoId);

  return (
    <div className="max-w-6xl mx-auto p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="Dependency Analysis"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <StatCard label="Dependency Score" value={`${data.overall_score}/100`} />
      </div>

      <MarkdownViewer content={data.summary} className="mb-8" />

      {data.circular_dependencies.length > 0 && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4 text-red-600">Circular Dependencies</h2>
          <div className="space-y-3">
            {data.circular_dependencies.map((cycle, i) => (
              <div key={i} className="border border-red-200 rounded-xl p-4 bg-red-50">
                {cycle.join(" → ")}
              </div>
            ))}
          </div>
        </div>
      )}

      {data.highly_coupled_modules.length > 0 && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4">Highly Coupled Modules</h2>
          <div className="space-y-3">
            {data.highly_coupled_modules.map((mod, i) => (
              <div key={i} className="border rounded-xl p-4 bg-white">
                <p className="font-semibold">{mod.module}</p>
                <p className="text-gray-600 mt-1">{mod.reason}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Recommendations</h2>
        <ul className="list-disc pl-6 space-y-2">
          {data.recommendations.map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
