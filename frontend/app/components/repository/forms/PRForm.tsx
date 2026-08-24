"use client";

import { useState } from "react";
import { generatePRDescription } from "@/app/lib/repository";
import { Loader2, GitPullRequest } from "lucide-react";
import ReactMarkdown from "react-markdown";

export default function PRForm({ repoId }: { repoId: number }) {
    const [title, setTitle] = useState("");
    const [summary, setSummary] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!title.trim() || !summary.trim()) return;

        setLoading(true);
        setResult(null);
        try {
            const res = await generatePRDescription(repoId, title, summary);
            // The backend returns a response model with 'description' or 'markdown'
            setResult(res.description || res.markdown || "No description generated.");
        } catch (err) {
            console.error(err);
            setResult("Error generating PR description. Ensure the repository is indexed.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col md:flex-row gap-6 p-6">
            {/* Form Section */}
            <div className="flex-1 max-w-md bg-white border border-[var(--border)] rounded-xl p-6 shadow-sm">
                <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600">
                        <GitPullRequest size={20} />
                    </div>
                    <div>
                        <h3 className="font-semibold text-gray-900">PR Description</h3>
                        <p className="text-sm text-gray-500">Automate your pull request template</p>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Issue / PR Title</label>
                        <input
                            type="text"
                            className="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                            placeholder="e.g. feat: add authentication pipeline"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            disabled={loading}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Implementation Summary</label>
                        <textarea
                            className="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none min-h-[120px] resize-none"
                            placeholder="Briefly describe what changes were made and why..."
                            value={summary}
                            onChange={(e) => setSummary(e.target.value)}
                            disabled={loading}
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={!title.trim() || !summary.trim() || loading}
                        className="w-full py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:bg-gray-400 flex items-center justify-center"
                    >
                        {loading ? <Loader2 className="animate-spin mr-2" size={18} /> : null}
                        {loading ? "Generating..." : "Generate Description"}
                    </button>
                </form>
            </div>

            {/* Result Section */}
            <div className="flex-2 flex-grow bg-white border border-[var(--border)] rounded-xl p-6 shadow-sm min-h-[400px]">
                <h3 className="font-semibold text-gray-900 mb-4 border-b pb-2">Generated Output</h3>
                {result ? (
                    <div className="prose prose-sm max-w-none text-gray-700">
                        <ReactMarkdown>{result}</ReactMarkdown>
                    </div>
                ) : (
                    <div className="h-full flex flex-col items-center justify-center text-gray-400 py-20">
                        <GitPullRequest size={32} className="mb-3 opacity-20" />
                        <p>Fill out the form to generate a structured PR format.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
