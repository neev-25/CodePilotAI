import Link from "next/link";

import ErrorCard from "@/app/components/repository/ErrorCard";
import MarkdownViewer from "@/app/components/repository/MarkdownViewer";
import ReportLayout from "@/app/components/repository/ReportLayout";
import {
  getProjectAssessment,
  getRepository,
  type ProjectAssessment,
} from "@/app/lib/repository";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function ProjectAssessmentPage({ params }: Props) {
  const { id } = await params;
  const repositoryId = Number(id);
  const repository = await getRepository(repositoryId);
  let assessment: ProjectAssessment;
  try {
    assessment = await getProjectAssessment(repositoryId);
  } catch {
    return (
      <ErrorCard
        title="Project assessment could not be generated"
        backHref={`/repositories/${repositoryId}`}
      />
    );
  }

  return (
    <ReportLayout
        repoId={repositoryId}
        repoName={repository.name}
        title="Project Assessment"
        subtitle="Product value and engineering quality, grounded in repository evidence"
        filename={`${repository.name}-project-assessment.pdf`}
    >
        <section>
          <MarkdownViewer content={assessment.assessment} />
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-5">
          <h2 className="mb-4 text-sm font-semibold text-slate-900">
            Repository evidence
          </h2>
          <div className="grid gap-3 md:grid-cols-2">
            {assessment.sources.map((source, index) => (
              <Link
                key={`${source.file}:${source.start_line}:${index}`}
                href={`/repositories/${repositoryId}/files?file=${encodeURIComponent(source.file)}`}
                className="rounded-lg border border-slate-200 p-4 transition hover:border-indigo-300"
              >
                <p className="font-mono text-sm font-semibold text-indigo-700">
                  {source.file}:{source.start_line}-{source.end_line}
                </p>
                <pre className="mt-3 overflow-x-auto whitespace-pre-wrap text-xs leading-5 text-slate-600">
                  {source.snippet}
                </pre>
              </Link>
            ))}
          </div>
        </section>
    </ReportLayout>
  );
}
