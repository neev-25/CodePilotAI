import type { ReactNode } from "react";

import PdfExportButton from "@/app/components/PdfExportButton";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";

interface Props {
  repoId: number;
  repoName: string;
  title: string;
  subtitle: string;
  filename: string;
  showExport?: boolean;
  children: ReactNode;
}

export default function ReportLayout({
  repoId,
  repoName,
  title,
  subtitle,
  filename,
  showExport = true,
  children,
}: Props) {
  return (
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-8 md:px-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <RepositoryHeader
          repoId={repoId}
          repoName={repoName}
          title={title}
          subtitle={subtitle}
        />
        {showExport && (
          <PdfExportButton targetId="report-content" filename={filename} />
        )}
      </div>
      <div
        id="report-content"
        className="space-y-6 rounded-2xl border border-slate-200 bg-slate-50 p-4 md:p-6"
      >
        <div className="rounded-xl border border-slate-200 bg-white px-5 py-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-indigo-600">
            Repository analysis
          </p>
          <h2 className="mt-1 text-xl font-bold text-slate-900">{title}</h2>
          <p className="mt-1 text-sm text-slate-500">{repoName}</p>
        </div>
        {children}
      </div>
    </main>
  );
}
