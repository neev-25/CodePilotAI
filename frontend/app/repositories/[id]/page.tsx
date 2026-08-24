import {
  getRepository,
  getRepositoryStats,
  getRepositorySummary,
} from "@/app/lib/repository";
import ReactMarkdown from "react-markdown";
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

  let summary: { summary: string } | null = null;
  try {
    summary = await getRepositorySummary(repoId);
  } catch {
    summary = null;
  }

  const actions = [
    { title: "AI Chat", description: "Query RAG indices about this repository.", href: "chat" },
    { title: "File Explorer", description: "Browse and analyze repository files.", href: "files" },
    { title: "Security Analysis", description: "Find vulnerabilities and security issues.", href: "security" },
    { title: "Repository Review", description: "AI code review of the repository.", href: "review" },
    { title: "README Generator", description: "Generate professional README.", href: "readme" },
    { title: "Architecture", description: "Explain repository architecture.", href: "architecture" },
    { title: "Dependency Graph", description: "Visualize file dependencies.", href: "dependency-graph" },
    { title: "Dependency Analysis", description: "Analyze coupling and circular deps.", href: "dependency-analysis" },
    { title: "Sequence Diagram", description: "Generate sequence diagram.", href: "sequence" },
    { title: "Class Diagram", description: "Generate class diagram.", href: "class-diagram" },
    { title: "Flowchart", description: "Generate flowchart.", href: "flowchart" },
    { title: "Complexity Analysis", description: "Analyze code complexity.", href: "complexity" },
    { title: "Health Score", description: "Overall repository health.", href: "health" },
    { title: "Production Readiness", description: "Production readiness report.", href: "production" },
    { title: "Refactoring Advisor", description: "Suggest improvements.", href: "refactor" },
    { title: "Test Generator", description: "Generate unit tests.", href: "tests" },
    { title: "AI Git Diff Review", description: "Evaluate local patches for bugs/optimizations.", href: "diff-review" },
    { title: "Change Impact Analysis", description: "Evaluate blast radius for local changes.", href: "change-impact" },
    { title: "Architecture Drift", description: "Audit constrained structural decay.", href: "architecture-drift" },
    { title: "Tasks & Collaboration", description: "Track LLM bugs onto persistent tickets.", href: "tasks" },
    { title: "PR Description", description: "Generate Pull Request description.", href: "pr" },
    { title: "Commit Message", description: "Generate Conventional Commit.", href: "commit" },
    { title: "Changelog", description: "Generate changelog entry.", href: "changelog" },
    { title: "Semantic Search", description: "Ask questions about the code.", href: "search" },
  ];

  return (
    <div className="mx-auto max-w-6xl">
      <h1 className="text-4xl font-bold">{repo.name}</h1>
      <p className="text-gray-500 mt-2">{repo.github_url}</p>

      <div className="mt-4">
        <span
          className={`px-3 py-1 rounded text-sm font-medium ${repo.status === "INDEXED"
            ? "bg-green-100 text-green-800"
            : repo.status === "FAILED"
              ? "bg-red-100 text-red-800"
              : "bg-blue-100 text-blue-800"
            }`}
        >
          {repo.status}
        </span>
      </div>
      <IndexRepositoryButton repositoryId={repo.id} status={repo.status} />

      <div className="mt-8">
        <h2 className="text-2xl font-bold">Repository Statistics</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <StatCard label="Total Files" value={stats.files} />
          <StatCard label="Lines of Code" value={stats.loc ?? 0} />
          <StatCard label="Commits" value={stats.commits ?? 0} />
          <StatCard label="Branches" value={stats.branches ?? 0} />
          <StatCard label="Contributors" value={stats.contributors ?? 0} />
          <StatCard label="Indexed Documents" value={stats.documents ?? 0} />
          <StatCard label="Chunks" value={stats.chunks ?? 0} />
          <StatCard label="Vectors" value={stats.vectors ?? 0} />
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-xl font-bold mb-4">Languages</h2>
        <div className="space-y-2">
          {Object.entries(stats.languages).map(([name, count]) => (
            <div
              key={name}
              className="flex justify-between border rounded-lg p-3 bg-white"
            >
              <span>{name}</span>
              <span className="text-gray-500">{count} files</span>
            </div>
          ))}
        </div>
      </div>

      {summary && (
        <div className="mt-10">
          <h2 className="text-2xl font-bold mb-5">Repository Summary</h2>
          <div className="border rounded-xl bg-white p-6 shadow-sm prose prose-gray max-w-none">
            <ReactMarkdown>{summary.summary}</ReactMarkdown>
          </div>
        </div>
      )}

      <div className="mt-12">
        <h2 className="text-2xl font-bold mb-6">AI Tools</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
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
