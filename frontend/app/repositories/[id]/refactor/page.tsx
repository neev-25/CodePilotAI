import { getRepository, getRefactorAdvice } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import MarkdownViewer from "@/app/components/repository/MarkdownViewer";
import StatCard from "@/app/components/repository/StatCard";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function RefactorPage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);
  const repo = await getRepository(repoId);
  const data = await getRefactorAdvice(repoId);

  return (
    <div className="max-w-6xl mx-auto p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="Refactoring Advisor"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <StatCard label="Refactor Score" value={`${data.overall_score}/100`} />
      </div>

      <MarkdownViewer content={data.summary} className="mb-8" />

      <h2 className="text-2xl font-bold mb-4">Suggestions</h2>
      <div className="space-y-4">
        {data.suggestions.map((s, i) => (
          <div key={i} className="border rounded-xl p-5 bg-white">
            <div className="flex justify-between items-start">
              <span className="font-bold text-orange-600 uppercase text-sm">
                {s.priority}
              </span>
              <span className="text-sm text-gray-500">{s.file}</span>
            </div>
            <p className="mt-3 font-semibold">{s.reason}</p>
            <p className="text-gray-600 mt-2">{s.recommendation}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
