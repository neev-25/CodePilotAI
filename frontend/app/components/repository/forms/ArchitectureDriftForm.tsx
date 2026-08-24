"use client";

import { useState } from "react";
import { measureArchitectureDrift } from "@/app/lib/repository";
import { Loader2, Construction } from "lucide-react";
import ReactMarkdown from "react-markdown";

export default function ArchitectureDriftForm({ repoId }: { repoId: number }) {
    const [constraint, setConstraint] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!constraint.trim()) return;

        setLoading(true);
        setResult(null);
        try {
            const res = await measureArchitectureDrift(repoId, constraint);
            setResult(res.drift_report || "No drift analysis generated.");
        } catch (err) {
            console.error(err);
            setResult("Error evaluating architecture drift. Ensure the repository is indexed.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col xl:flex-row gap-6 p-6">
            <div className="flex-1 max-w-md bg-white border border-[var(--border)] rounded-xl p-6 shadow-sm">
                <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600">
                        <Construction size={20} />
                    </div>
                    <div>
                        <h3 className="font-semibold text-gray-900">Drift Constraints</h3>
                        <p className="text-sm text-gray-500">Isolate architectural deviations natively.</p>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Architectural Rule / Constraint</label>
                        <textarea
                            className="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none min-h-[220px] resize-none text-sm"
                            placeholder="E.g. Frontend react components should never import backend python utilities..."
                            value={constraint}
                            onChange={(e) => setConstraint(e.target.value)}
                            disabled={loading}
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={!constraint.trim() || loading}
                        className="w-full py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:bg-gray-400 flex items-center justify-center"
                    >
                        {loading ? <Loader2 className="animate-spin mr-2" size={18} /> : null}
                        {loading ? "Scanning Codebase..." : "Check Architecture"}
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
                        <Construction size={32} className="mb-3 opacity-20" />
                        <p>Define an organizational code constraint to generate a decay report.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
