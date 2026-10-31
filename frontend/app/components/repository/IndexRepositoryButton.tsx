"use client";

import { useEffect, useRef, useState } from "react";
import { LoaderCircle, Play, RefreshCw } from "lucide-react";
import { useRouter } from "next/navigation";
import {
  getLatestIndexJob,
  indexRepository,
  type IndexingJob,
} from "@/app/lib/repository";

interface Props {
  repositoryId: number;
  status: string;
}

export default function IndexRepositoryButton({ repositoryId, status }: Props) {
  const router = useRouter();
  const [isIndexing, setIsIndexing] = useState(false);
  const [indexingStarted, setIndexingStarted] = useState(status === "INDEXING");
  const [error, setError] = useState("");
  const [job, setJob] = useState<IndexingJob | null>(null);
  const requestInFlight = useRef(false);
  const indexed = status === "INDEXED";

  useEffect(() => {
    if (status !== "INDEXING" && !indexingStarted) {
      if (status !== "FAILED") return;
      void getLatestIndexJob(repositoryId)
        .then((latestJob) => {
          setJob(latestJob);
        })
        .catch(() => setError("Could not load the last indexing job details."));
      return;
    }
    const timer = window.setInterval(async () => {
      try {
        const latestJob = await getLatestIndexJob(repositoryId);
        setJob(latestJob);
        if (["COMPLETED", "FAILED", "PAUSED"].includes(latestJob.status)) {
          window.clearInterval(timer);
          setIndexingStarted(false);
          router.refresh();
        }
      } catch {
        setError("Could not refresh indexing progress. Indexing continues in the backend.");
      }
    }, 2500);
    void getLatestIndexJob(repositoryId).then(setJob).catch(() => undefined);
    return () => window.clearInterval(timer);
  }, [indexingStarted, repositoryId, router, status]);

  async function handleIndex() {
    if (requestInFlight.current || indexingStarted || status === "INDEXING") return;
    requestInFlight.current = true;
    setError("");
    setIsIndexing(true);
    try {
      const response = await indexRepository(repositoryId);
      if (response.status === "COMPLETED" || response.status === "FAILED") {
        setIndexingStarted(false);
      } else {
        setIndexingStarted(true);
      }
      setJob({
        id: response.job_id,
        status: response.status,
        message: response.message,
        result: null,
      });
      router.refresh();
    } catch (caught) {
      const detail = caught && typeof caught === "object" && "response" in caught
        ? (caught as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : undefined;
      setError(detail ?? "Indexing failed. Check that the repository is accessible and try again.");
    } finally {
      requestInFlight.current = false;
      setIsIndexing(false);
    }
  }

  const busy =
    isIndexing ||
    indexingStarted ||
    status === "INDEXING" ||
    job?.status === "QUEUED" ||
    job?.status === "RUNNING" ||
    job?.status === "RETRYING";
  const progress = job?.result;
  const progressMessage =
    typeof progress?.message === "string" ? progress.message : job?.message;
  const embeddedChunks =
    typeof progress?.embedded_chunks === "number" ? progress.embedded_chunks : null;
  const totalChunks =
    typeof progress?.total_chunks === "number" ? progress.total_chunks : null;

  return <div className="mt-5">
    <button onClick={handleIndex} disabled={busy} className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60">
      {busy ? <LoaderCircle className="animate-spin" size={17}/> : indexed ? <RefreshCw size={17}/> : <Play size={17}/>}
      {busy ? "Indexing repository…" : indexed ? "Re-index repository" : "Index repository"}
    </button>
    {job && (busy || job.status === "PAUSED" || job.status === "FAILED") && (
      <div className="mt-3 max-w-xl rounded-xl border border-[var(--border)] bg-[var(--bg-panel)] p-3 text-sm text-[var(--fg-muted)]">
        <p>{progressMessage}</p>
        {embeddedChunks !== null && totalChunks !== null && (
          <p className="mt-1">
            Embedded {embeddedChunks} of {totalChunks} chunks
            {typeof progress?.pending_chunks === "number" &&
              ` · ${progress.pending_chunks} pending`}
          </p>
        )}
        {job.status === "PAUSED" && (
          <p className="mt-1 font-medium text-amber-600">
            Progress is saved. Retry indexing after the Gemini quota resets.
          </p>
        )}
      </div>
    )}
    {error && <p role="alert" className="mt-3 max-w-xl text-sm text-rose-600">{error}</p>}
    {!indexed && !busy && <p className="mt-2 text-sm text-slate-500">Indexing reads supported source files and prepares them for search and AI analysis.</p>}
  </div>;
}
