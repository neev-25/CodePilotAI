"use client";

import { useEffect, useState } from "react";
import { LoaderCircle, Play, RefreshCw } from "lucide-react";
import { useRouter } from "next/navigation";
import { getRepository, indexRepository } from "@/app/lib/repository";

interface Props {
  repositoryId: number;
  status: string;
}

export default function IndexRepositoryButton({ repositoryId, status }: Props) {
  const router = useRouter();
  const [isIndexing, setIsIndexing] = useState(false);
  const [error, setError] = useState("");
  const indexed = status === "INDEXED";

  useEffect(() => {
    if (status !== "INDEXING") return;
    const timer = window.setInterval(async () => {
      try {
        const repository = await getRepository(repositoryId);
        if (repository.status !== "INDEXING") { window.clearInterval(timer); router.refresh(); }
      } catch { /* retain the current visible state and let the next poll retry */ }
    }, 2500);
    return () => window.clearInterval(timer);
  }, [repositoryId, router, status]);

  async function handleIndex() {
    if (isIndexing) return;
    setError("");
    setIsIndexing(true);
    try {
      await indexRepository(repositoryId);
      router.refresh();
    } catch (caught) {
      const detail = caught && typeof caught === "object" && "response" in caught
        ? (caught as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : undefined;
      setError(detail ?? "Indexing failed. Check that the repository is accessible and try again.");
    } finally {
      setIsIndexing(false);
    }
  }

  return <div className="mt-5">
    <button onClick={handleIndex} disabled={isIndexing || status === "INDEXING"} className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60">
      {isIndexing || status === "INDEXING" ? <LoaderCircle className="animate-spin" size={17}/> : indexed ? <RefreshCw size={17}/> : <Play size={17}/>} 
      {isIndexing || status === "INDEXING" ? "Indexing repository…" : indexed ? "Re-index repository" : "Index repository"}
    </button>
    {error && <p role="alert" className="mt-3 max-w-xl text-sm text-rose-600">{error}</p>}
    {!indexed && !isIndexing && <p className="mt-2 text-sm text-slate-500">Indexing reads supported source files and prepares them for search and AI analysis.</p>}
  </div>;
}
