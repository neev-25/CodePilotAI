"use client";

import { useEffect, useId, useState } from "react";
import mermaid from "mermaid";

interface Props {
  chart: string;
}

export default function MermaidViewer({ chart }: Props) {
  const instanceId = useId().replace(/:/g, "");
  const [svg, setSvg] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: "strict",
      theme: "default",
    });

    mermaid
      .render(`diagram-${instanceId}`, chart)
      .then(({ svg: renderedSvg }) => {
        if (active) {
          setSvg(renderedSvg);
          setError("");
        }
      })
      .catch(() => {
        if (active) {
          setSvg("");
          setError("The generated Mermaid source could not be rendered.");
        }
      });

    return () => {
      active = false;
    };
  }, [chart, instanceId]);

  return (
    <section className="overflow-hidden rounded-xl border border-slate-200 bg-white">
      <div className="border-b border-slate-200 px-5 py-3">
        <h2 className="text-sm font-semibold text-slate-700">Diagram preview</h2>
      </div>
      {svg ? (
        <div
          className="overflow-x-auto p-6 [&_svg]:mx-auto [&_svg]:max-w-full"
          dangerouslySetInnerHTML={{ __html: svg }}
        />
      ) : (
        <div className="space-y-3 p-5">
          {error && <p className="text-sm text-amber-700">{error}</p>}
          <pre className="overflow-x-auto rounded-lg bg-slate-950 p-4 text-sm text-slate-100">
            <code>{chart}</code>
          </pre>
        </div>
      )}
    </section>
  );
}
