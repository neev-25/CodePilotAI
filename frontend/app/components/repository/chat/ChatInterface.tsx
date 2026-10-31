"use client";

import { useState, useRef, useEffect } from "react";
import { askRepository, AskResponse } from "@/app/lib/repository";
import ReactMarkdown from "react-markdown";
import { Send, Bot, User, Loader2, FileCode2 } from "lucide-react";
import Link from "next/link";
import PdfExportButton from "@/app/components/PdfExportButton";

interface Message {
    role: "user" | "assistant";
    content: string;
    sources?: AskResponse["sources"];
}

export default function ChatInterface({ repoId }: { repoId: number }) {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: "assistant",
            content: "Hello! I am CodePilot AI. You can ask me anything about this repository's structure, logic, or dependencies.",
        },
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, loading]);

    async function handleSend() {
        if (!input.trim() || loading) return;

        const userMessage: Message = { role: "user", content: input };
        setMessages((prev) => [...prev, userMessage]);
        const currentInput = input;
        setInput("");
        setLoading(true);

        try {
            const res = await askRepository(repoId, currentInput);
            setMessages((prev) => [
                ...prev,
                { role: "assistant", content: res.answer, sources: res.sources },
            ]);
        } catch {
            setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    content: "Sorry, I encountered an error answering your question. Please make sure the repository is fully indexed.",
                },
            ]);
        } finally {
            setLoading(false);
        }
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="flex flex-col h-full">
            <div className="flex items-center justify-between border-b border-[var(--border)] bg-white px-5 py-3">
                <div>
                    <h2 className="text-sm font-semibold text-slate-800">Repository conversation</h2>
                    <p className="text-xs text-slate-500">Answers include links to retrieved source evidence.</p>
                </div>
                <PdfExportButton
                    targetId="chat-transcript"
                    filename={`repository-${repoId}-conversation.pdf`}
                />
            </div>
            <div id="chat-transcript" className="flex-1 overflow-y-auto p-6 space-y-6 bg-[var(--surface-50)]">
                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`flex gap-4 max-w-[85%] ${msg.role === "user" ? "ml-auto flex-row-reverse" : "mr-auto"
                            }`}
                    >
                        <div
                            className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${msg.role === "user" ? "bg-indigo-600 text-white" : "bg-blue-100 text-blue-600"
                                }`}
                        >
                            {msg.role === "user" ? <User size={16} /> : <Bot size={16} />}
                        </div>

                        <div className="flex flex-col gap-2 min-w-0 flex-1">
                            <div
                                className={`rounded-2xl p-4 shadow-sm prose prose-sm max-w-none ${msg.role === "user"
                                        ? "bg-indigo-600 text-white [&_*]:text-white prose-a:text-indigo-100"
                                        : "bg-white border border-[var(--border)]"
                                    }`}
                            >
                                <ReactMarkdown>{msg.content}</ReactMarkdown>
                            </div>

                            {/* Citations block */}
                            {msg.sources && msg.sources.length > 0 && (
                                <div className="mt-2 space-y-2">
                                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Citations</p>
                                    <div className="grid gap-2 grid-cols-1 sm:grid-cols-2">
                                        {msg.sources.map((src, i) => (
                                            <Link
                                                key={i}
                                                href={`/repositories/${repoId}/files?file=${encodeURIComponent(src.file)}`}
                                                className="flex items-center gap-2 p-2 rounded-lg border border-[var(--border)] bg-gray-50 hover:bg-white hover:border-indigo-300 transition-colors text-sm"
                                                title={src.snippet}
                                            >
                                                <FileCode2 size={14} className="text-gray-400 shrink-0" />
                                                <span className="truncate flex-1 font-medium text-gray-700">
                                                    {src.file}:{src.start_line}-{src.end_line}
                                                </span>
                                            </Link>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex gap-4 max-w-[85%] mr-auto">
                        <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-blue-100 text-blue-600">
                            <Bot size={16} />
                        </div>
                        <div className="rounded-2xl p-4 shadow-sm bg-white border border-[var(--border)] flex items-center gap-2 text-gray-500">
                            <Loader2 size={16} className="animate-spin" /> Thinking...
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="p-4 border-t border-[var(--border)] bg-white shrink-0">
                <div className="max-w-4xl mx-auto relative rounded-xl border border-[var(--border)] shadow-sm focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-indigo-500">
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask a question about the repository..."
                        className="w-full resize-none bg-transparent border-0 py-4 pl-4 pr-14 focus:ring-0 sm:text-sm min-h-[60px] max-h-[200px]"
                        rows={1}
                        disabled={loading}
                    />
                    <button
                        onClick={handleSend}
                        disabled={!input.trim() || loading}
                        className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg bg-indigo-600 text-white disabled:opacity-50 disabled:bg-gray-400 hover:bg-indigo-700 transition-colors"
                    >
                        <Send size={16} />
                    </button>
                </div>
            </div>
        </div>
    );
}
