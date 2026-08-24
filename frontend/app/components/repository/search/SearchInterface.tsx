"use client";

import { useState } from "react";
import { semanticSearch } from "@/app/lib/repository";
import { Search, MapPin, Code2, Loader2 } from "lucide-react";
import CodeViewer from "@/app/components/repository/CodeViewer";
import Link from "next/link";

interface SearchHit {
    content: string;
    path: string;
    start_line: number;
    end_line: number;
    distance: number;
}

export default function SearchInterface({ repoId }: { repoId: number }) {
    const [query, setQuery] = useState("");
    const [hits, setHits] = useState<SearchHit[]>([]);
    const [loading, setLoading] = useState(false);
    const [searched, setSearched] = useState(false);

    const handleSearch = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!query.trim() || loading) return;

        setLoading(true);
        setSearched(true);
        setHits([]);

        try {
            const res = await semanticSearch(repoId, query);
            setHits(res.hits || []);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full overflow-hidden">
            <div className="p-6 border-b border-[var(--border)] bg-white shrink-0">
                <form
                    onSubmit={handleSearch}
                    className="max-w-4xl mx-auto relative rounded-xl border border-[var(--border)] shadow-sm focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-indigo-500 bg-white"
                >
                    <div className="flex items-center">
                        <Search className="ml-4 text-gray-400 shrink-0" size={20} />
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Search concepts, logic, or functions..."
                            className="w-full bg-transparent border-0 py-4 px-4 focus:ring-0 sm:text-base outline-none"
                            disabled={loading}
                        />
                        <button
                            type="submit"
                            disabled={!query.trim() || loading}
                            className="mr-2 p-2 px-4 rounded-lg bg-indigo-600 text-white font-medium disabled:opacity-50 hover:bg-indigo-700 transition"
                        >
                            {loading ? <Loader2 className="animate-spin" size={20} /> : "Search"}
                        </button>
                    </div>
                </form>
            </div>

            <div className="flex-1 overflow-y-auto p-4 md:p-8 bg-[var(--surface-50)]">
                <div className="max-w-5xl mx-auto space-y-6">
                    {loading && (
                        <div className="flex flex-col items-center justify-center py-20 text-indigo-500 gap-4">
                            <Loader2 className="animate-spin" size={32} />
                            <p className="text-gray-500">Searching through index...</p>
                        </div>
                    )}

                    {!loading && searched && hits.length === 0 && (
                        <div className="text-center py-20 text-gray-500">
                            No semantic hits found for this phrase. Try rephrasing or checking if the repository is indexed.
                        </div>
                    )}

                    {!loading && hits.map((hit, idx) => {
                        const ext = hit.path.split(".").pop() || "typescript";
                        return (
                            <div key={idx} className="bg-white rounded-xl border border-[var(--border)] overflow-hidden shadow-sm">
                                <div className="border-b border-[var(--border)] bg-gray-50/50 p-4 flex items-center justify-between">
                                    <div className="flex items-center gap-3 w-full pr-4">
                                        <Code2 className="text-indigo-500 shrink-0" size={18} />
                                        <span className="font-semibold text-gray-800 truncate" title={hit.path}>
                                            {hit.path}
                                        </span>
                                        <span className="bg-indigo-100 text-indigo-700 font-medium px-2 py-0.5 rounded text-xs shrink-0 inline-flex items-center gap-1">
                                            <MapPin size={12} /> Lines {hit.start_line}-{hit.end_line}
                                        </span>
                                    </div>
                                    <div className="shrink-0 flex items-center gap-4">
                                        <div className="flex items-center gap-1.5 text-xs font-semibold px-2 py-1 bg-gray-100 rounded text-gray-500">
                                            {(hit.distance).toFixed(3)}
                                        </div>
                                        <Link
                                            href={`/repositories/${repoId}/files?file=${encodeURIComponent(hit.path)}`}
                                            className="px-3 py-1.5 bg-white border border-gray-200 shadow-sm text-sm font-medium rounded-lg hover:border-indigo-300 hover:text-indigo-600 transition"
                                        >
                                            View in Explorer
                                        </Link>
                                    </div>
                                </div>
                                <div className="p-0 max-h-[300px] overflow-hidden relative group">
                                    <CodeViewer code={hit.content} language={ext} />
                                    <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-[var(--surface-100)] to-transparent pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity" />
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
