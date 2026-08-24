"use client";

import { useState } from "react";
import { generateChangelog } from "@/app/lib/repository";
import { Loader2, FileText } from "lucide-react";
import ReactMarkdown from "react-markdown";

export default function ChangelogForm({ repoId }: { repoId: number }) {
  const [version, setVersion] = useState("");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!version.trim() || !summary.trim()) return;

    setLoading(true);
    setResult(null);
    try {
      const res = await generateChangelog(repoId, version, summary);
      setResult(res.changelog || res.markdown || "No changelog generated.");
    } catch (err) {
      console.error(err);
      setResult("Error generating changelog. Ensure the repository is indexed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col xl:flex-row gap-6 p-6">
      {/* Form Section */}
      <div className="flex-1 max-w-md bg-white border border-[var(--border)] rounded-xl p-6 shadow-sm">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600">
            <FileText size={20} />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Changelog Entry</h3>
            <p className="text-sm text-gray-500">Draft automated version histories</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Version Title/Number</label>
            <input
              type="text"
              className="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
              placeholder="e.g. v1.4.0"
              value={version}
              onChange={(e) => setVersion(e.target.value)}
              disabled={loading}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Version Abstract (Key Changes)</label>
            <textarea
              className="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none min-h-[120px] resize-none"
              placeholder="Briefly state what was pushed in this version..."
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              disabled={loading}
            />
          </div>
          <button
            type="submit"
            disabled={!version.trim() || !summary.trim() || loading}
            className="w-full py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:bg-gray-400 flex items-center justify-center"
          >
            {loading ? <Loader2 className="animate-spin mr-2" size={18} /> : null}
            {loading ? "Drafting Changelog..." : "Generate Entry"}
          </button>
        </form>
      </div>

      {/* Result */}
      <div className="flex-[2] bg-white border border-[var(--border)] rounded-xl p-6 shadow-sm min-h-[400px]">
        <h3 className="font-semibold text-gray-900 mb-4 border-b pb-2">Changelog Output</h3>
        {result ? (
          <div className="prose prose-sm max-w-none text-gray-700 max-h-[600px] overflow-y-auto pr-2">
            <ReactMarkdown>{result}</ReactMarkdown>
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-gray-400 py-20">
            <FileText size={32} className="mb-3 opacity-20" />
            <p>Populate the forms to map the repository index into a Changelog draft.</p>
          </div>
        )}
      </div>
    </div>
  );
}
