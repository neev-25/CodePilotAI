"use client";

import { useState } from "react";
import { generateChangelog } from "@/app/lib/repository";
import MarkdownViewer from "../MarkdownViewer";

interface Props {
  repoId: number;
}

export default function ChangelogForm({ repoId }: Props) {
  const [version, setVersion] = useState("");
  const [summary, setSummary] = useState("");
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!version.trim() || !summary.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await generateChangelog(repoId, version, summary);
      setResult(data.changelog);
    } catch {
      setError("Failed to generate changelog.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit} className="border rounded-xl p-6 bg-white space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Version</label>
          <input
            type="text"
            value={version}
            onChange={(e) => setVersion(e.target.value)}
            className="w-full border rounded-lg px-4 py-2"
            placeholder="1.2.0"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Change Summary</label>
          <textarea
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            className="w-full border rounded-lg px-4 py-2 h-24"
            placeholder="Added new features, fixed bugs..."
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Generating..." : "Generate Changelog"}
        </button>
      </form>
      {error && <p className="mt-4 text-red-600">{error}</p>}
      {result && (
        <div className="mt-8">
          <MarkdownViewer content={result} />
        </div>
      )}
    </div>
  );
}
