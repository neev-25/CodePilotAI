import ReactMarkdown from "react-markdown";

interface Props {
  content: string;
  className?: string;
}

export default function MarkdownViewer({ content, className = "" }: Props) {
  // Use regex lookahead to split the markdown at each H2 heading.
  // This physically turns the output into modular cards rather than a single unified text blob.
  const sections = (content || "").split(/(?=^##\s+)/m).filter(s => s.trim().length > 0);

  return (
    <div className={`space-y-4 ${className}`}>
      {sections.map((section, idx) => (
        <div
          key={idx}
          className="prose prose-slate max-w-none rounded-xl border border-slate-200 bg-white p-5 shadow-sm md:p-7 prose-headings:tracking-tight prose-h1:text-2xl prose-h2:border-b prose-h2:border-slate-100 prose-h2:pb-3 prose-h2:text-lg prose-h3:text-base prose-p:leading-7 prose-li:leading-7 prose-pre:rounded-lg prose-pre:bg-slate-950"
        >
          <ReactMarkdown>{section}</ReactMarkdown>
        </div>
      ))}
    </div>
  );
}
