import { getRepository } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import ChatInterface from "@/app/components/repository/chat/ChatInterface";

type Props = {
    params: Promise<{ id: string }>;
};

export default async function ChatPage({ params }: Props) {
    const { id } = await params;
    const repoId = Number(id);
    const repo = await getRepository(repoId);

    return (
        <div className="max-w-5xl mx-auto p-4 md:p-8 h-[calc(100vh-6rem)] flex flex-col">
            <RepositoryHeader
                repoId={repoId}
                repoName={repo.name}
                title="AI Chat"
                subtitle={`Query RAG indices across ${repo.name}`}
            />

            <div className="flex-1 mt-6 overflow-hidden rounded-xl border border-[var(--border)] bg-gray-50 shadow-sm flex flex-col">
                <ChatInterface repoId={repoId} />
            </div>
        </div>
    );
}
