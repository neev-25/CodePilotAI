import { getRepository, getComplexityAnalysis } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import MarkdownViewer from "@/app/components/repository/MarkdownViewer";
import StatCard from "@/app/components/repository/StatCard";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function ComplexityPage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);
  const repo = await getRepository(repoId);
  const data = await getComplexityAnalysis(repoId);

  return (
    <div className="max-w-6xl mx-auto p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="Complexity Analysis"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <StatCard label="Complexity Score" value={`${data.overall_score}/100`} />
      </div>

      <MarkdownViewer content={data.summary} className="mb-8" />

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="border rounded-xl p-6 bg-white">
          <h3 className="font-semibold text-gray-500 mb-2">Maintainability</h3>
          <p>{data.maintainability}</p>
        </div>
        <div className="border rounded-xl p-6 bg-white">
          <h3 className="font-semibold text-gray-500 mb-2">Technical Debt</h3>
          <p>{data.technical_debt}</p>
        </div>
      </div>

      {data.complex_files.length > 0 && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4">Complex Files</h2>
          <div className="space-y-3">
            {data.complex_files.map((f, i) => (
              <div key={i} className="border rounded-xl p-4 bg-white">
                <div className="flex justify-between">
                  <span className="font-semibold">{f.file}</span>
                  <span className="text-orange-600 text-sm">{f.complexity}</span>
                </div>
                <p className="text-gray-600 mt-2">{f.reason}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {data.code_smells.length > 0 && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4">Code Smells</h2>
          <ul className="list-disc pl-6 space-y-2">
            {data.code_smells.map((smell, i) => (
              <li key={i}>{smell}</li>
            ))}
          </ul>
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
