import Link from "next/link";

interface Props {
  title?: string;
  message?: string;
  backHref?: string;
}

export default function ErrorCard({
  title = "Something went wrong",
  message = "Please try again or go back to the repository.",
  backHref,
}: Props) {
  return (
    <div className="max-w-6xl mx-auto p-8">
      <div className="border border-red-200 rounded-xl bg-red-50 p-8">
        <h1 className="text-2xl font-bold text-red-600">{title}</h1>
        <p className="mt-3 text-gray-600">{message}</p>
        {backHref && (
          <Link
            href={backHref}
            className="inline-block mt-6 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Go Back
          </Link>
        )}
      </div>
    </div>
  );
}
