import { getRepository } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import ChangeImpactForm from "@/app/components/repository/forms/ChangeImpactForm";

type Props = { params: Promise<{ id: string }> };

export default async function ChangeImpactPage({ params }: Props) {
    const { id } = await params;
    const repoId = Number(id);
    const repo = await getRepository(repoId);

    return (
        <div className="max-w-6xl mx-auto p-4 md:p-8 h-[calc(100vh-6rem)] flex flex-col">
            <RepositoryHeader
                repoId={repoId}
                repoName={repo.name}
                title="Change Impact Analysis"
                subtitle="Forensics mapping architectural fallout caused by targeted logical drifting."
            />
            <div className="mt-6 flex-1 bg-gray-50 rounded-xl border border-[var(--border)] shadow-sm overflow-y-auto">
                <ChangeImpactForm repoId={repoId} />
            </div>
        </div>
    );
}
