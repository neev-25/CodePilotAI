import { getRepository, getHealthScore } from "@/app/lib/repository";
import MarkdownViewer from "@/app/components/repository/MarkdownViewer";
import ReportLayout from "@/app/components/repository/ReportLayout";
import StatCard from "@/app/components/repository/StatCard";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function HealthPage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);
  const repo = await getRepository(repoId);
  const data = await getHealthScore(repoId);

  return (
    <ReportLayout
        repoId={repoId}
        repoName={repo.name}
        title="Repository Health Score"
        subtitle="A structured overview of maintainability, security, architecture, and complexity."
        filename={`${repo.name}-engineering-health.pdf`}
    >

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
        <StatCard label="Overall Score" value={`${data.overall_score}/100`} color="text-blue-600" />
        <StatCard label="Grade" value={data.grade} color="text-green-600" />
        <StatCard label="Maintainability" value={data.maintainability_score} />
        <StatCard label="Security" value={data.security_score} />
        <StatCard label="Architecture" value={data.architecture_score} />
        <StatCard label="Complexity" value={data.complexity_score} />
      </div>

      <MarkdownViewer content={data.summary} className="mb-8" />

      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <h2 className="text-xl font-bold mb-4 text-green-700">Strengths</h2>
          <div className="space-y-2">
            {data.strengths.map((s, i) => (
              <div key={i} className="border rounded-lg p-3 bg-green-50">{s}</div>
            ))}
          </div>
        </div>
        <div>
          <h2 className="text-xl font-bold mb-4 text-red-700">Weaknesses</h2>
          <div className="space-y-2">
            {data.weaknesses.map((w, i) => (
              <div key={i} className="border rounded-lg p-3 bg-red-50">{w}</div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Priority Actions</h2>
        <ul className="list-disc pl-6 space-y-2">
          {data.priority_actions.map((a, i) => (
            <li key={i}>{a}</li>
          ))}
        </ul>
      </div>
    </ReportLayout>
  );
}
