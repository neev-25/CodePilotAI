import axios from "axios";
import ErrorCard from "@/app/components/repository/ErrorCard";
import ReportLayout from "@/app/components/repository/ReportLayout";
import {
  getProductionReadiness,
  getRepository,
  type ProductionReadiness,
} from "@/app/lib/repository";

type Props = {
  params: Promise<{ id: string }>;
};

const reviewAreas = [
  ["Scalability", "scalability"],
  ["Maintainability", "maintainability"],
  ["Security", "security"],
  ["Testing", "testing"],
  ["Observability", "observability"],
  ["Deployment", "deployment"],
] as const;

const actionCards = [
  {
    title: "Release blockers",
    key: "blockers",
    headingClass: "text-rose-700",
  },
  { title: "Risks to review", key: "risks", headingClass: "text-amber-700" },
  {
    title: "Recommended actions",
    key: "recommendations",
    headingClass: "text-indigo-700",
  },
] as const;

export default async function ProductionReadinessPage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);
  const repository = await getRepository(repoId);
  let report: ProductionReadiness;
  try {
    report = await getProductionReadiness(repoId);
  } catch (error) {
    let message =
      "The backend could not complete the production-readiness request.";
    if (axios.isAxiosError(error)) {
      const data: unknown = error.response?.data;
      if (
        data &&
        typeof data === "object" &&
        "detail" in data &&
        typeof data.detail === "string"
      ) {
        message = data.detail;
      } else if (error.response) {
        message = `The backend returned HTTP ${error.response.status}. Check the backend logs for the production-readiness request.`;
      } else {
        message =
          "Could not reach the backend. Confirm it is running and try again.";
      }
    }

    return (
      <div className="mx-auto max-w-6xl p-8">
        <ErrorCard
          title="Production readiness request failed"
          message={message}
          backHref={`/repositories/${repoId}`}
        />
      </div>
    );
  }

  return (
    <ReportLayout
      repoId={repoId}
      repoName={repository.name}
      title="Production Readiness"
      subtitle="A cautious release review grounded in repository configuration and source evidence."
      filename={`${repository.name}-production-readiness.pdf`}
    >
      <section className="grid gap-4 sm:grid-cols-[auto_1fr]">
        <div className="flex min-w-36 flex-col items-center justify-center rounded-xl border border-slate-200 bg-white p-6">
          <span className="text-4xl font-bold tracking-tight text-slate-900">
            {report.production_score}
          </span>
          <span className="mt-1 text-xs font-medium uppercase tracking-wide text-slate-500">
            Readiness score
          </span>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={`rounded-full px-3 py-1 text-xs font-semibold ${
                report.go_live
                  ? "bg-emerald-100 text-emerald-800"
                  : "bg-amber-100 text-amber-800"
              }`}
            >
              {report.go_live ? "Go-live supported" : "Go-live not confirmed"}
            </span>
            <span className="text-sm font-semibold text-slate-700">
              {report.readiness}
            </span>
          </div>
          <p className="mt-3 text-sm leading-6 text-slate-600">{report.summary}</p>
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-sm font-semibold text-slate-900">
          Readiness by area
        </h2>
        <div className="grid gap-3 md:grid-cols-2">
          {reviewAreas.map(([label, key]) => (
            <article
              key={key}
              className="rounded-xl border border-slate-200 bg-white p-4"
            >
              <h3 className="text-sm font-semibold text-slate-800">{label}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                {report[key]}
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-sm font-semibold text-slate-900">
          Repository evidence
        </h2>
        <p className="mt-1 text-xs text-slate-500">
          File presence is inspected; tests and deployments are not executed.
        </p>
        <div className="mt-4 divide-y divide-slate-100">
          {report.evidence.map((item) => (
            <article
              key={item.area}
              className="grid gap-2 py-3 sm:grid-cols-[180px_100px_1fr]"
            >
              <h3 className="text-sm font-medium text-slate-800">{item.area}</h3>
              <span
                className={`w-fit rounded-full px-2 py-1 text-[11px] font-semibold uppercase ${
                  item.status === "present"
                    ? "bg-emerald-50 text-emerald-700"
                    : item.status === "partial"
                      ? "bg-amber-50 text-amber-700"
                      : "bg-slate-100 text-slate-600"
                }`}
              >
                {item.status}
              </span>
              <div>
                <p className="text-sm leading-5 text-slate-600">{item.detail}</p>
                {item.files.length > 0 && (
                  <p className="mt-1 break-all font-mono text-xs text-slate-400">
                    {item.files.join(", ")}
                  </p>
                )}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        {actionCards.map(({ title, key, headingClass }) => (
          <article
            key={title}
            className="rounded-xl border border-slate-200 bg-white p-5"
          >
            <h2 className={`text-sm font-semibold ${headingClass}`}>{title}</h2>
            {report[key].length > 0 ? (
              <ul className="mt-3 space-y-2">
                {report[key].map((item, index) => (
                  <li
                    key={`${item}-${index}`}
                    className="rounded-lg bg-slate-50 p-3 text-sm leading-5 text-slate-700"
                  >
                    {item}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-3 text-sm text-slate-500">None identified.</p>
            )}
          </article>
        ))}
      </section>
    </ReportLayout>
  );
}
