"use client";

import { useState } from "react";
import { generateChangeImpact } from "@/app/lib/repository";
import { Loader2, Zap } from "lucide-react";
import ReactMarkdown from "react-markdown";

export default function ChangeImpactForm({ repoId }: { repoId: number }) {
    const [filePath, setFilePath] = useState("");
    const [proposedChange, setProposedChange] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!filePath.trim() || !proposedChange.trim()) return;

        setLoading(true);
        setResult(null);
        try {
            const res = await generateChangeImpact(repoId, filePath, proposedChange);
            setResult(res.impact || "No impact analysis generated.");
        } catch (err) {
            console.error(err);
            setResult("Error generating impact analysis. Ensure the repository is indexed.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col xl:flex-row gap-6 p-6">
            <div className="flex-1 max-w-md bg-white border border-[var(--border)] rounded-xl p-6 shadow-sm">
                <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600">
                        <Zap size={20} />
                    </div>
                    <div>
                        <h3 className="font-semibold text-gray-900">Blast Radius</h3>
                        <p className="text-sm text-gray-500">Determine system impacts of specific file changes.</p>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Target File Path</label>
                        <input
                            type="text"
                            className="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none font-mono text-sm"
                            placeholder="src/backend/auth.ts"
                            value={filePath}
                            onChange={(e) => setFilePath(e.target.value)}
                            disabled={loading}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Proposed Change Summary</label>
                        <textarea
                            className="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none min-h-[160px] resize-none text-sm"
                            placeholder="I plan to rewrite the JWT signing verification and add a redis cache check for revoked tokens..."
                            value={proposedChange}
                            onChange={(e) => setProposedChange(e.target.value)}
                            disabled={loading}
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={!filePath.trim() || !proposedChange.trim() || loading}
                        className="w-full py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:bg-gray-400 flex items-center justify-center"
                    >
                        {loading ? <Loader2 className="animate-spin mr-2" size={18} /> : null}
                        {loading ? "Analyzing Impact..." : "Evaluate Impact"}
                    </button>
                </form>
            </div>

            <div className="flex-[2] bg-white border border-[var(--border)] rounded-xl p-6 shadow-sm min-h-[500px]">
                <h3 className="font-semibold text-gray-900 mb-4 border-b pb-2">Analysis Results</h3>
                {result ? (
                    <div className="prose prose-sm max-w-none text-gray-700 max-h-[800px] overflow-y-auto pr-2">
                        <ReactMarkdown>{result}</ReactMarkdown>
                    </div>
                ) : (
                    <div className="h-full flex flex-col items-center justify-center text-gray-400 py-20">
                        <Zap size={32} className="mb-3 opacity-20" />
                        <p>Declare a file and a proposed change sequence to generate a blast radius report.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
