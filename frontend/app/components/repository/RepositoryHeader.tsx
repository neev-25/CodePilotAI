import Link from "next/link";
import { ArrowLeft } from "lucide-react";

interface Props {
  repoId: number;
  repoName?: string;
  title: string;
  subtitle?: string;
}

export default function RepositoryHeader({
  repoId,
  repoName,
  title,
  subtitle,
}: Props) {
  return (
    <div className="mb-8">
      <Link
        href={`/repositories/${repoId}`}
        className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-blue-600 mb-4"
      >
        <ArrowLeft className="w-4 h-4" />
        {repoName ? `Back to ${repoName}` : "Back to Repository"}
      </Link>
      <h1 className="text-4xl font-bold">{title}</h1>
      {subtitle && <p className="text-gray-500 mt-2">{subtitle}</p>}
    </div>
  );
}
