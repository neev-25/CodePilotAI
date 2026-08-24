import Link from "next/link";

interface Props {
  title: string;
  description: string;
  href: string;
}

export default function RepositoryActionCard({
  title,
  description,
  href,
}: Props) {
  return (
    <Link href={href}>
      <div className="border rounded-xl p-5 hover:border-blue-500 hover:shadow-lg transition cursor-pointer bg-white">
        <h3 className="font-bold text-lg">{title}</h3>

        <p className="text-gray-500 mt-2">{description}</p>
      </div>
    </Link>
  );
}
