import { getRepository, getSecurityAnalysis } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import IssueCard from "@/app/components/repository/IssueCard";
import StatCard from "@/app/components/repository/StatCard";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function SecurityPage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);
  const repo = await getRepository(repoId);
  const analysis = await getSecurityAnalysis(repoId);

  return (
    <div className="max-w-6xl mx-auto p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="Security Analysis"
      />

      <div className="mb-8">
        <StatCard label="Risk Score" value={`${analysis.risk_score}/100`} color="text-red-600" />
      </div>

      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Security Issues</h2>
        <div className="space-y-4">
          {analysis.security.map((issue, index) => (
            <IssueCard
              key={index}
              severity={issue.severity}
              file={issue.file}
              line={issue.line}
              title={issue.issue}
            />
          ))}
        </div>
      </div>

      <div className="mt-10">
        <h2 className="text-2xl font-bold mb-4">Bugs</h2>
        <div className="space-y-4">
          {analysis.bugs.map((bug, index) => (
            <IssueCard
              key={index}
              severity={bug.severity}
              file={bug.file}
              line={bug.line}
              title={bug.issue}
              description={bug.explanation}
            />
          ))}
        </div>
      </div>

      <div className="mt-10">
        <h2 className="text-2xl font-bold mb-4">Reliability</h2>
        <div className="space-y-4">
          {analysis.reliability.map((item, index) => (
            <IssueCard
              key={index}
              severity={item.severity}
              file={item.file}
              line={item.line}
              title={item.issue}
              description={item.explanation}
            />
          ))}
        </div>
      </div>

      <div className="mt-10">
        <h2 className="text-2xl font-bold mb-4">Recommendations</h2>
        <ul className="list-disc pl-6 space-y-2">
          {analysis.recommendations.map((r, index) => (
            <li key={index}>{r}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
