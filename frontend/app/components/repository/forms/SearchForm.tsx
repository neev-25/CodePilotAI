"use client";

import { useState } from "react";
import { askRepository } from "@/app/lib/repository";
import MarkdownViewer from "../MarkdownViewer";

interface Props {
  repoId: number;
}

export default function SearchForm({ repoId }: Props) {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<{
    answer: string;
    sources: { file: string; start_line: number; end_line: number; snippet: string }[];
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await askRepository(repoId, question);
      setResult(data);
    } catch {
      setError("Failed to search repository.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit} className="border rounded-xl p-6 bg-white space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Ask a question about the code</label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="w-full border rounded-lg px-4 py-2 h-24"
            placeholder="How does authentication work?"
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </form>
      {error && <p className="mt-4 text-red-600">{error}</p>}
      {result && (
        <div className="mt-8 space-y-6">
          <MarkdownViewer content={result.answer} />
          {result.sources.length > 0 && (
            <div>
              <h3 className="text-xl font-bold mb-4">Sources</h3>
              <div className="space-y-3">
                {result.sources.map((src, i) => (
                  <div key={i} className="border rounded-xl p-4 bg-white">
                    <p className="font-semibold text-sm">
                      {src.file}:{src.start_line}-{src.end_line}
                    </p>
                    <pre className="mt-2 text-sm bg-gray-50 rounded p-3 overflow-x-auto">
                      {src.snippet}
                    </pre>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
