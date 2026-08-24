"use client";

import { Trash2 } from "lucide-react";
import type { Repository } from "@/app/lib/repository";

interface Props {
  repository: Repository;

  onDelete: () => void;
}

export default function RepositoryCard({
  repository,

  onDelete,
}: Props) {
  return (
    <div className="panel group rounded-2xl p-5 transition hover:border-indigo-200 hover:shadow-md">
      <div className="flex justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2"><h2 className="font-bold text-xl text-slate-800 group-hover:text-indigo-700">{repository.name}</h2><span className={`rounded-full px-2.5 py-1 text-[11px] font-bold tracking-wide ${repository.status === "INDEXED" ? "bg-emerald-50 text-emerald-700" : repository.status === "FAILED" ? "bg-rose-50 text-rose-700" : "bg-amber-50 text-amber-700"}`}>{repository.status}</span></div>

          <p className="mt-2 truncate text-sm text-slate-500">{repository.github_url}</p>
        </div>

        <button
          onClick={(event) => {
            event.preventDefault();
            event.stopPropagation();
            onDelete();
          }}
          aria-label={`Delete ${repository.name}`}
          className="rounded-lg p-2 text-slate-400 transition hover:bg-rose-50 hover:text-rose-600"
        >
          <Trash2 />
        </button>
      </div>
    </div>
  );
}
