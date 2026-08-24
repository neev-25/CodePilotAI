"use client";

import { useState } from "react";
import { generatePRDescription } from "@/app/lib/repository";
import MarkdownViewer from "../MarkdownViewer";

interface Props {
  repoId: number;
}

export default function PRDescriptionForm({ repoId }: Props) {
  const [title, setTitle] = useState("");
  const [summary, setSummary] = useState("");
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await generatePRDescription(repoId, title, summary);
      setResult(data.markdown);
    } catch {
      setError("Failed to generate PR description.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit} className="border rounded-xl p-6 bg-white space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">PR Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full border rounded-lg px-4 py-2"
            placeholder="Add user authentication"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Summary (optional)</label>
          <textarea
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            className="w-full border rounded-lg px-4 py-2 h-24"
            placeholder="Brief description of changes..."
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Generating..." : "Generate PR Description"}
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
