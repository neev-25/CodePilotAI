interface Props {
  severity: string;
  file?: string;
  line?: number;
  title: string;
  description?: string;
}

const severityColors: Record<string, string> = {
  critical: "text-red-700",
  high: "text-red-600",
  medium: "text-orange-500",
  low: "text-yellow-600",
  info: "text-blue-600",
};

export default function IssueCard({
  severity,
  file,
  line,
  title,
  description,
}: Props) {
  const color = severityColors[severity.toLowerCase()] ?? "text-gray-600";

  return (
    <div className="border rounded-xl p-5 bg-white">
      <div className="flex justify-between items-start">
        <span className={`font-bold uppercase text-sm ${color}`}>
          {severity}
        </span>
        {file && (
          <span className="text-sm text-gray-500">
            {file}
            {line !== undefined ? `:${line}` : ""}
          </span>
        )}
      </div>
      <h3 className="font-semibold mt-3">{title}</h3>
      {description && <p className="text-gray-600 mt-2">{description}</p>}
    </div>
  );
}
