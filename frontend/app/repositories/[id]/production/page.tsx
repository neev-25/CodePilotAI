import { getRepository, getProductionReadiness } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import MarkdownViewer from "@/app/components/repository/MarkdownViewer";
import StatCard from "@/app/components/repository/StatCard";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function ProductionPage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);
  const repo = await getRepository(repoId);
  const data = await getProductionReadiness(repoId);

  return (
    <div className="max-w-6xl mx-auto p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="Production Readiness"
      />

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
        <StatCard
          label="Production Score"
          value={`${data.production_score}/100`}
          color="text-blue-600"
        />
        <StatCard label="Readiness" value={data.readiness} />
        <StatCard
          label="Go Live"
          value={data.go_live ? "Yes" : "No"}
          color={data.go_live ? "text-green-600" : "text-red-600"}
        />
      </div>

      <MarkdownViewer content={data.summary} className="mb-8" />

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {[
          { label: "Scalability", value: data.scalability },
          { label: "Maintainability", value: data.maintainability },
          { label: "Security", value: data.security },
          { label: "Testing", value: data.testing },
          { label: "Observability", value: data.observability },
          { label: "Deployment", value: data.deployment },
        ].map((item) => (
          <div key={item.label} className="border rounded-xl p-5 bg-white">
            <h3 className="font-semibold text-gray-500 text-sm">{item.label}</h3>
            <p className="mt-2">{item.value}</p>
          </div>
        ))}
      </div>

      {data.blockers.length > 0 && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4 text-red-600">Blockers</h2>
          <div className="space-y-2">
            {data.blockers.map((b, i) => (
              <div key={i} className="border border-red-200 rounded-lg p-3 bg-red-50">{b}</div>
            ))}
          </div>
        </div>
      )}

      {data.risks.length > 0 && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4">Risks</h2>
          <ul className="list-disc pl-6 space-y-2">
            {data.risks.map((r, i) => (
              <li key={i}>{r}</li>
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
