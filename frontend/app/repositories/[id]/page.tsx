import {
  getRepository,
  getRepositoryStats,
} from "@/app/lib/repository";
import RepositoryActionCard from "@/app/components/repository/actions/RepositoryActionCard";
import StatCard from "@/app/components/repository/StatCard";
import IndexRepositoryButton from "@/app/components/repository/IndexRepositoryButton";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function RepositoryPage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);

  const repo = await getRepository(repoId);
  const stats = await getRepositoryStats(repoId);

  const actions = [
    { title: "Project Assessment", description: "Evaluate user value and engineering quality with source citations.", href: "assessment" },
    { title: "Codebase Q&A", description: "Ask questions and inspect retrieved source evidence.", href: "chat" },
    { title: "Engineering Health", description: "Prioritized maintainability, security, and architecture signals.", href: "health" },
    { title: "Security Analysis", description: "Review security, reliability, and bug findings.", href: "security" },
    { title: "Production Readiness", description: "Review release risks and verifiable operational evidence.", href: "production-readiness" },
    { title: "Dependency Map", description: "Explore modules and their relationships.", href: "dependency-graph" },
    { title: "Developer Onboarding", description: "Build a practical guide to the repository.", href: "onboarding" },
    { title: "Test Case Generator", description: "Generate framework-aware tests from a selected source file.", href: "test-generator" },
    { title: "Sequence Diagram", description: "Visualize evidenced request and service interactions.", href: "sequence" },
    { title: "Class Diagram", description: "Visualize classes, models, and their relationships.", href: "class-diagram" },
    { title: "Application Flowchart", description: "Trace the main flow through the codebase.", href: "flowchart" },
    { title: "Browse Source", description: "Inspect indexed files and cited code.", href: "files" },
  ];

  return (
    <div className="mx-auto max-w-6xl font-sans text-slate-800">
      <div className="border-b pb-6 mb-8">
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">{repo.name}</h1>
        <p className="text-slate-500 mt-2 font-mono text-sm">{repo.github_url}</p>

        <div className="mt-5">
          <span
            className={`px-3 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase ${repo.status === "INDEXED"
              ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
              : repo.status === "FAILED"
                ? "bg-red-100 text-red-800 border border-red-200"
                : "bg-blue-100 text-blue-800 border border-blue-200"
              }`}
          >
            {repo.status}
          </span>
        </div>
      </div>

      <IndexRepositoryButton repositoryId={repo.id} status={repo.status} />

      <div className="mt-12">
        <h2 className="text-xl font-semibold border-b pb-2 mb-6">Repository Statistics</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <StatCard label="Total Files" value={stats.files} />
          <StatCard label="Lines of Code" value={stats.loc ?? 0} />
          <StatCard label="Commits" value={stats.commits ?? 0} />
          <StatCard label="Contributors" value={stats.contributors ?? 0} />
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-8 mt-12">
        <div>
          <h2 className="text-xl font-semibold border-b pb-2 mb-6">Tech Stack Breakdown</h2>
          <div className="space-y-3">
            {Object.entries(stats.languages).map(([name, count]) => (
              <div
                key={name}
                className="flex justify-between border-b pb-2 text-sm"
              >
                <span className="font-medium text-slate-700">{name}</span>
                <span className="text-slate-500">{count} files</span>
              </div>
            ))}
          </div>
        </div>

      </div>

      <div className="mt-16 bg-slate-50 p-8 rounded-xl border border-slate-200">
        <h2 className="text-2xl font-bold mb-2 text-slate-800">Project Insights</h2>
        <p className="mb-8 text-sm text-slate-600">
          Start with a cited product and engineering assessment, then explore focused tools.
        </p>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {actions.map((action) => (
            <RepositoryActionCard
              key={action.href}
              title={action.title}
              description={action.description}
              href={`/repositories/${repo.id}/${action.href}`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
