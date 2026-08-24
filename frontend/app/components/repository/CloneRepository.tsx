"use client";

import { useState } from "react";

interface Props {
  onClone: (url: string) => Promise<void>;
}

export default function CloneRepository({ onClone }: Props) {
  const [url, setUrl] = useState("");
  const [isCloning, setIsCloning] = useState(false);
  const [error, setError] = useState("");

  async function submit() {
    if (!url.trim() || isCloning) return;
    setError(""); setIsCloning(true);
    try { await onClone(url.trim()); setUrl(""); } catch { setError("Could not clone this repository. Check the URL and backend connection."); } finally { setIsCloning(false); }
  }

  return (
    <div className="panel rounded-2xl p-6">
      <p className="eyebrow">Repository workspace</p><h2 className="mt-1 text-xl font-bold text-slate-800">Connect a repository</h2><p className="mt-1 text-sm text-slate-500">Paste a public GitHub URL to create a fresh AI workspace.</p>

      <div className="flex gap-3 mt-5">
        <input
          className="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition placeholder:text-slate-400 focus:border-indigo-400 focus:ring-4 focus:ring-indigo-100"
          placeholder="GitHub Repository URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />

        <button
          onClick={submit} disabled={isCloning || !url.trim()}
          className="rounded-xl bg-indigo-600 px-6 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isCloning ? "Connecting…" : "Connect"}
        </button>
      </div>
      {error && <p role="alert" className="mt-3 text-sm text-rose-600">{error}</p>}
    </div>
  );
}
