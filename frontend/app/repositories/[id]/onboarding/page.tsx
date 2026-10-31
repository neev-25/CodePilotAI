import { getRepository, getOnboarding } from "@/app/lib/repository";
import MarkdownViewer from "@/app/components/repository/MarkdownViewer";
import ErrorCard from "@/app/components/repository/ErrorCard";
import ReportLayout from "@/app/components/repository/ReportLayout";

type Props = {
    params: Promise<{ id: string }>;
};

export default async function OnboardingPage({ params }: Props) {
    const { id } = await params;
    const repoId = Number(id);
    const repo = await getRepository(repoId);

    const data = await getOnboarding(repoId).catch(() => null);

    if (!data) {
        return (
            <ErrorCard
                title="Failed to Analyze Onboarding Data"
                backHref={`/repositories/${id}`}
            />
        );
    }

    return (
        <ReportLayout
            repoId={repoId}
            repoName={repo.name}
            title="Developer Onboarding Guide"
            subtitle="A practical, code-grounded introduction to this repository."
            filename={`${repo.name}-onboarding-guide.pdf`}
        >
                <MarkdownViewer content={data.markdown} />
        </ReportLayout>
    );
}
