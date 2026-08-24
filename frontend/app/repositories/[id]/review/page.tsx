import { getRepository, getRepositoryReview } from "@/app/lib/repository";
import RepositoryHeader from "@/app/components/repository/RepositoryHeader";
import MarkdownViewer from "@/app/components/repository/MarkdownViewer";
import StatCard from "@/app/components/repository/StatCard";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function ReviewPage({ params }: Props) {
  const { id } = await params;
  const repoId = Number(id);
  const repo = await getRepository(repoId);
  const review = await getRepositoryReview(repoId);

  return (
    <div className="max-w-6xl mx-auto p-8">
      <RepositoryHeader
        repoId={repoId}
        repoName={repo.name}
        title="Repository Review"
      />

      <div className="mb-8">
        <StatCard label="Overall Score" value={`${review.overall_score}/10`} color="text-blue-600" />
      </div>

      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Strengths</h2>
        <div className="space-y-3">
          {review.strengths.map((item, index) => (
            <div key={index} className="border rounded-lg p-4 bg-green-50">{item}</div>
          ))}
        </div>
      </div>

      <div className="mt-10">
        <h2 className="text-2xl font-bold mb-4">Issues</h2>
        <div className="space-y-4">
          {review.issues.map((issue, index) => (
            <div key={index} className="border rounded-xl p-5 bg-white">
              <div className="flex justify-between">
                <span className="font-bold text-red-600">{issue.severity.toUpperCase()}</span>
                <span className="text-sm text-gray-500">{issue.file}</span>
              </div>
              <p className="mt-3 font-semibold">{issue.category}</p>
              <p className="text-gray-600 mt-2">{issue.message}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-10">
        <h2 className="text-2xl font-bold mb-4">Recommendations</h2>
        <ul className="list-disc pl-6 space-y-2">
          {review.recommendations.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      </div>

      <div className="mt-10">
        <h2 className="text-2xl font-bold mb-4">Overall Review</h2>
        <MarkdownViewer content={review.overall_review} />
      </div>
    </div>
  );
}
