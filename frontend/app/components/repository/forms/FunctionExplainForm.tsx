"use client";

import { useState } from "react";
import { explainFunction } from "@/app/lib/repository";
import MarkdownViewer from "../MarkdownViewer";

interface Props {
  repoId: number;
  filePath: string;
}

export default function FunctionExplainForm({ repoId, filePath }: Props) {
  const [functionName, setFunctionName] = useState("");
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!functionName.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await explainFunction(repoId, filePath, functionName);
      setResult(data.explanation);
    } catch {
      setError("Failed to explain function.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit} className="border rounded-xl p-6 bg-white space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Function Name</label>
          <input
            type="text"
            value={functionName}
            onChange={(e) => setFunctionName(e.target.value)}
            className="w-full border rounded-lg px-4 py-2"
            placeholder="handleLogin"
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Explaining..." : "Explain Function"}
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
