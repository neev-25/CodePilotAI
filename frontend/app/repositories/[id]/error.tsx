"use client";

import Link from "next/link";
import { AlertTriangle, RefreshCw } from "lucide-react";

export default function RepositoryError({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return <div className="mx-auto flex max-w-xl flex-col items-start py-16">
    <span className="grid h-12 w-12 place-items-center rounded-2xl bg-rose-50 text-rose-600"><AlertTriangle size={24}/></span>
    <p className="eyebrow mt-6">Repository workspace</p>
    <h1 className="mt-2 text-2xl font-bold text-slate-800">This request could not be completed</h1>
    <p className="mt-3 leading-7 text-slate-600">Check that the backend is running, the repository is indexed, and your Gemini API key is configured. You can safely retry after correcting the issue.</p>
    <div className="mt-6 flex gap-3"><button onClick={reset} className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700"><RefreshCw size={16}/> Retry</button><Link href="/repositories" className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50">All repositories</Link></div>
  </div>;
}
