import ReactMarkdown from "react-markdown";

interface Props {
  content: string;
  className?: string;
}

export default function MarkdownViewer({ content, className = "" }: Props) {
  return (
    <div
      className={`prose prose-gray max-w-none border rounded-xl bg-white shadow-sm p-8 ${className}`}
    >
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
}
