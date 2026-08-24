"use client";

import { useState, useEffect } from "react";
import { getTasks, createTask } from "@/app/lib/repository";
import { Loader2, Plus, KanbanSquare, CheckCircle2, Circle } from "lucide-react";

export default function TasksForm({ repoId }: { repoId: number }) {
    const [tasks, setTasks] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [creating, setCreating] = useState(false);

    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");

    const loadTasks = async () => {
        try {
            setLoading(true);
            const data = await getTasks(repoId);
            setTasks(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadTasks();
    }, [repoId]);

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!title.trim()) return;

        setCreating(true);
        try {
            await createTask(repoId, title, description);
            setTitle("");
            setDescription("");
            await loadTasks();
        } catch (err) {
            console.error(err);
        } finally {
            setCreating(false);
        }
    };

    return (
        <div className="flex flex-col lg:flex-row gap-6 p-6">
            {/* List View */}
            <div className="flex-[2] bg-white border border-[var(--border)] rounded-xl p-6 shadow-sm min-h-[500px]">
                <div className="flex items-center gap-3 mb-6 border-b pb-4">
                    <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600">
                        <KanbanSquare size={20} />
                    </div>
                    <div>
                        <h3 className="font-semibold text-gray-900">Task Backlog</h3>
                        <p className="text-sm text-gray-500">Persistent intelligent architecture tracker</p>
                    </div>
                </div>

                {loading ? (
                    <div className="flex justify-center items-center h-48">
                        <Loader2 className="animate-spin text-gray-400" size={32} />
                    </div>
                ) : tasks.length === 0 ? (
                    <div className="flex flex-col items-center justify-center text-gray-400 py-16">
                        <KanbanSquare size={32} className="mb-3 opacity-20" />
                        <p>No tasks mapped currently. Log architectural drifts safely.</p>
                    </div>
                ) : (
                    <div className="space-y-3 max-h-[600px] overflow-y-auto">
                        {tasks.map(task => (
                            <div key={task.id} className="p-4 border rounded-lg hover:border-indigo-300 transition bg-gray-50 flex items-start gap-4">
                                {task.status === "CLOSED" ? (
                                    <CheckCircle2 className="text-green-500 mt-0.5" size={18} />
                                ) : (
                                    <Circle className="text-gray-400 mt-0.5" size={18} />
                                )}
                                <div>
                                    <h4 className="font-semibold text-gray-900 text-sm mb-1">{task.title}</h4>
                                    {task.description && <p className="text-sm text-gray-600 mb-2">{task.description}</p>}
                                    <p className="text-xs text-gray-400">Created: {new Date(task.created_at).toLocaleDateString()}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Creation Pane */}
            <div className="flex-1 max-w-sm bg-white border border-[var(--border)] rounded-xl p-6 shadow-sm h-fit">
                <h3 className="font-semibold text-gray-900 mb-4 pb-2 border-b">Create New Task</h3>
                <form onSubmit={handleCreate} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Issue Title</label>
                        <input
                            type="text"
                            className="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none text-sm"
                            placeholder="Fix cross-domain leak..."
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            disabled={creating}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Description & Context</label>
                        <textarea
                            className="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none min-h-[120px] text-sm resize-none"
                            placeholder="Based on the Architect Drift log, we need to map..."
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            disabled={creating}
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={!title.trim() || creating}
                        className="w-full py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 flex items-center justify-center text-sm"
                    >
                        {creating ? <Loader2 className="animate-spin mr-2" size={16} /> : <Plus size={16} className="mr-2" />}
                        Create Ticket
                    </button>
                </form>
            </div>
        </div>
    );
}
