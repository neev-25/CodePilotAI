"use client";

import { useState } from "react";
import { generateTests } from "@/app/lib/repository";
import MarkdownViewer from "../MarkdownViewer";

interface Props {
  repoId: number;
  filePath?: string;
}

export default function TestGeneratorForm({ repoId, filePath }: Props) {
  const [path, setPath] = useState(filePath ?? "");
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!path.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await generateTests(repoId, path);
      setResult(data.tests);
    } catch {
      setError("Failed to generate tests.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit} className="border rounded-xl p-6 bg-white space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">File Path</label>
          <input
            type="text"
            value={path}
            onChange={(e) => setPath(e.target.value)}
            className="w-full border rounded-lg px-4 py-2 font-mono text-sm"
            placeholder="src/utils/helpers.py"
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Generating..." : "Generate Tests"}
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
