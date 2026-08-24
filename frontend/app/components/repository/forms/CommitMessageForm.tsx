"use client";

import { useState } from "react";
import { generateCommitMessage } from "@/app/lib/repository";

interface Props {
  repoId: number;
}

export default function CommitMessageForm({ repoId }: Props) {
  const [summary, setSummary] = useState("");
  const [result, setResult] = useState<{
    conventional_commit: string;
    detailed_commit: string;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!summary.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await generateCommitMessage(repoId, summary);
      setResult(data);
    } catch {
      setError("Failed to generate commit message.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit} className="border rounded-xl p-6 bg-white space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Change Summary</label>
          <textarea
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            className="w-full border rounded-lg px-4 py-2 h-24"
            placeholder="Fixed login bug and added password reset..."
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Generating..." : "Generate Commit Message"}
        </button>
      </form>
      {error && <p className="mt-4 text-red-600">{error}</p>}
      {result && (
        <div className="mt-8 space-y-6">
          <div className="border rounded-xl p-6 bg-white">
            <h3 className="font-semibold text-gray-500 mb-2">Conventional Commit</h3>
            <pre className="bg-gray-50 rounded-lg p-4 font-mono text-sm whitespace-pre-wrap">
              {result.conventional_commit}
            </pre>
          </div>
          <div className="border rounded-xl p-6 bg-white">
            <h3 className="font-semibold text-gray-500 mb-2">Detailed Commit</h3>
            <pre className="bg-gray-50 rounded-lg p-4 font-mono text-sm whitespace-pre-wrap">
              {result.detailed_commit}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
