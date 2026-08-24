"use client";

import { useState } from "react";
import { generateCommitMessage } from "@/app/lib/repository";
import { Loader2, GitCommit } from "lucide-react";

export default function CommitForm({ repoId }: { repoId: number }) {
    const [summary, setSummary] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!summary.trim()) return;

        setLoading(true);
        setResult(null);
        try {
            const res = await generateCommitMessage(repoId, summary);
            setResult(res.message || res.commit_message || "No commit message generated.");
        } catch (err) {
            console.error(err);
            setResult("Error generating commit message. Ensure the repository is indexed.");
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = () => {
        if (result) navigator.clipboard.writeText(result);
    };

    return (
        <div className="flex flex-col md:flex-row gap-6 p-6">
            {/* Form Section */}
            <div className="flex-1 max-w-md bg-white border border-[var(--border)] rounded-xl p-6 shadow-sm">
                <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600">
                        <GitCommit size={20} />
                    </div>
                    <div>
                        <h3 className="font-semibold text-gray-900">Commit Message</h3>
                        <p className="text-sm text-gray-500">Automate conventional commits</p>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Raw Diff / Changes Summary</label>
                        <textarea
                            className="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none min-h-[120px] resize-none"
                            placeholder="E.g., Added semantic search api routes to repository.ts and backend routers..."
                            value={summary}
                            onChange={(e) => setSummary(e.target.value)}
                            disabled={loading}
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={!summary.trim() || loading}
                        className="w-full py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:bg-gray-400 flex items-center justify-center"
                    >
                        {loading ? <Loader2 className="animate-spin mr-2" size={18} /> : null}
                        {loading ? "Generating..." : "Generate Commit"}
                    </button>
                </form>
            </div>

            {/* Result Section */}
            <div className="flex-2 flex-grow bg-white border border-[var(--border)] rounded-xl p-6 shadow-sm min-h-[300px] flex flex-col">
                <div className="flex items-center justify-between border-b pb-2 mb-4">
                    <h3 className="font-semibold text-gray-900">Generated Commit</h3>
                    {result && (
                        <button
                            onClick={copyToClipboard}
                            className="text-indigo-600 text-sm font-medium hover:text-indigo-700 px-2 py-1 rounded bg-indigo-50"
                        >
                            Copy to Clipboard
                        </button>
                    )}
                </div>

                {result ? (
                    <pre className="p-4 bg-gray-50 border border-gray-200 rounded-lg whitespace-pre-wrap font-mono text-sm text-gray-800">
                        {result}
                    </pre>
                ) : (
                    <div className="h-full flex flex-col items-center justify-center text-gray-400 py-20">
                        <GitCommit size={32} className="mb-3 opacity-20" />
                        <p>Fill out the summary to generate a standard commit.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
