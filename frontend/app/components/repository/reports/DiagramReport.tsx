import Link from "next/link";

import ErrorCard from "@/app/components/repository/ErrorCard";
import MermaidViewer from "@/app/components/repository/MermaidViewer";
import ReportLayout from "@/app/components/repository/ReportLayout";
import {
  getClassDiagram,
  getFlowchart,
  getRepository,
  getSequenceDiagram,
  type RepositoryDiagram,
} from "@/app/lib/repository";

type DiagramKind = "sequence" | "class" | "flowchart";

const diagramTitles: Record<DiagramKind, string> = {
  sequence: "Sequence Diagram",
  class: "Class Diagram",
  flowchart: "Application Flowchart",
};

interface Props {
  repoId: number;
  kind: DiagramKind;
}

export default async function DiagramReport({ repoId, kind }: Props) {
  const repository = await getRepository(repoId);
  let diagram: RepositoryDiagram;
  try {
    diagram =
      kind === "sequence"
        ? await getSequenceDiagram(repoId)
        : kind === "class"
          ? await getClassDiagram(repoId)
          : await getFlowchart(repoId);
  } catch {
    return (
      <div className="mx-auto max-w-6xl p-8">
        <ErrorCard
          title={`${diagramTitles[kind]} could not be generated. Confirm the repository is indexed and try again.`}
          backHref={`/repositories/${repoId}`}
        />
      </div>
    );
  }

  return (
    <ReportLayout
      repoId={repoId}
      repoName={repository.name}
      title={diagramTitles[kind]}
      subtitle="Generated from retrieved repository source, with evidence links."
      filename={`${repository.name}-${kind}-diagram.pdf`}
    >
      <MermaidViewer chart={diagram.mermaid} />
      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-sm font-semibold text-slate-800">Source evidence</h2>
        <div className="mt-3 flex flex-wrap gap-2">
          {diagram.sources.map((source) => (
            <Link
              key={`${source.file}:${source.start_line}`}
              href={`/repositories/${repoId}/files?file=${encodeURIComponent(source.file)}`}
              title={source.snippet}
              className="rounded-lg border border-indigo-100 bg-indigo-50 px-3 py-2 text-sm font-medium text-indigo-700 hover:border-indigo-300"
            >
              {source.file}:{source.start_line}-{source.end_line}
            </Link>
          ))}
        </div>
      </section>
    </ReportLayout>
  );
}
