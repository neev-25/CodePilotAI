"use client";

import { useEffect, useRef, useState, useMemo } from "react";
import mermaid from "mermaid";
import { Braces, ExternalLink, GitBranch, Network, RefreshCw, Code, Layout, Image, Palette, Download } from "lucide-react";
import ReactFlow, { Background, Controls, MarkerType, MiniMap, Position, type Edge, type Node } from "reactflow";

interface Props {
  chart: string;
  fallback?: boolean;
}

type DiagramKind = "flow" | "sequence" | "class";
type ViewMode = "mermaid" | "flowchart" | "raw";
type MermaidTheme = "hand-drawn" | "neutral" | "dark" | "forest";

function cleanMermaidCode(code: string): string {
  let cleaned = code.trim();
  cleaned = cleaned.replace(/^```(?:mermaid)?/i, "").replace(/```$/, "").trim();
  if (!cleaned || !/^(graph|flowchart|sequenceDiagram|classDiagram|erDiagram|gantt|pie|gitGraph|stateDiagram)/m.test(cleaned)) {
    return "graph TD\n  Web[Client Application] --> Gateway[API Gateway]\n  Gateway --> DB[(Database)]";
  }
  return cleaned;
}

function getKind(chart: string): DiagramKind {
  if (/^\s*sequenceDiagram/m.test(chart)) return "sequence";
  if (/^\s*classDiagram/m.test(chart)) return "class";
  return "flow";
}

const cleanLabel = (value: string) => value.replace(/["'\[\](){}]/g, "").trim().slice(0, 60);

function toReactFlowGraph(chart: string): { kind: DiagramKind; nodes: Node[]; edges: Edge[] } {
  const kind = getKind(chart);
  const labels = new Map<string, string>();
  const relations: Array<[string, string, string?]> = [];
  const register = (id: string, label?: string) => {
    if (!id || id.toLowerCase() === "subgraph" || id.toLowerCase() === "end") return;
    if (!labels.has(id)) labels.set(id, label ? cleanLabel(label) : cleanLabel(id));
  };

  if (kind === "sequence") {
    chart.split("\n").forEach((line) => {
      const participant = line.match(/^\s*participant\s+(\w+)(?:\s+as\s+(.+))?/);
      if (participant) register(participant[1], participant[2]);
      const message = line.match(/^\s*(\w+)\s*[-=]+>+\s*(\w+)\s*:\s*(.+)$/);
      if (message) {
        register(message[1]);
        register(message[2]);
        relations.push([message[1], message[2], cleanLabel(message[3])]);
      }
    });
  } else {
    chart.split("\n").forEach((line) => {
      const classMatch = line.match(/^\s*class\s+(\w+)/);
      if (classMatch) register(classMatch[1]);
      const definition = line.match(/^\s*(\w+)\s*(?:\[|\(|\{)\s*["']?([^\]})"']+)/);
      if (definition) register(definition[1], definition[2]);
      const link = line.match(/^\s*(\w+)\s*[-.o*<>]+>\s*(\w+)(?:\s*:\s*(.+))?/);
      if (link) {
        register(link[1]);
        register(link[2]);
        relations.push([link[1], link[2], link[3] ? cleanLabel(link[3]) : undefined]);
      }
    });
  }

  if (!labels.size) {
    register("Web", "Client App");
    register("Gateway", "API Gateway");
    register("DB", "Database");
    relations.push(["Web", "Gateway"], ["Gateway", "DB"]);
  }

  const items = [...labels.entries()];
  const nodes: Node[] = items.map(([id, label], index) => {
    const columnCount = kind === "sequence" ? Math.max(items.length, 1) : 3;
    const x = kind === "sequence" ? index * 210 : (index % columnCount) * 260;
    const y = kind === "sequence" ? (index % 2) * 180 : Math.floor(index / columnCount) * 150;
    return {
      id,
      position: { x, y },
      data: { label },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      style: {
        border: "1.5px solid #6366f1",
        borderRadius: 14,
        background: "#ffffff",
        boxShadow: "0 8px 20px rgba(30, 41, 59, .08)",
        color: "#0f172a",
        fontWeight: 650,
        fontSize: 13,
        padding: "12px 16px",
        minWidth: 145,
        textAlign: "center",
      },
    };
  });
  const edges: Edge[] = relations.map(([source, target, label], index) => ({
    id: `edge-${index}`,
    source,
    target,
    label,
    animated: true,
    markerEnd: { type: MarkerType.ArrowClosed, color: "#6366f1" },
    style: { stroke: "#6366f1", strokeWidth: 2 },
    labelStyle: { fill: "#475569", fontSize: 11, fontWeight: 600 },
    labelBgStyle: { fill: "#fff", fillOpacity: 0.9 },
  }));
  return { kind, nodes, edges };
}

export default function MermaidViewer({ chart, fallback = false }: Props) {
  const cleanedChart = useMemo(() => cleanMermaidCode(chart), [chart]);
  const [svgContent, setSvgContent] = useState<string | null>(null);
  const [renderError, setRenderError] = useState<boolean>(false);
  const [viewMode, setViewMode] = useState<ViewMode>("mermaid");
  const [mermaidTheme, setMermaidTheme] = useState<MermaidTheme>("hand-drawn");
  const containerRef = useRef<HTMLDivElement>(null);
  const graph = useMemo(() => toReactFlowGraph(cleanedChart), [cleanedChart]);

  const kind = graph.kind;
  const Icon = kind === "sequence" ? Network : kind === "class" ? Braces : GitBranch;
  const title = kind === "sequence" ? "Sequence Diagram" : kind === "class" ? "Class Diagram" : "Scalable Architecture Diagram";

  const cleanupMermaidErrorDOM = () => {
    if (typeof document === "undefined") return;
    document.querySelectorAll("[id^='dmermaid']").forEach((el) => el.remove());
    document.querySelectorAll(".mermaid-error").forEach((el) => el.remove());
  };

  useEffect(() => {
    cleanupMermaidErrorDOM();
    let isMounted = true;

    const renderDiagram = async () => {
      setRenderError(false);
      setSvgContent(null);
      const isHandDrawn = mermaidTheme === "hand-drawn";

      // 1st Attempt: Preferred Theme
      try {
        mermaid.initialize({
          startOnLoad: false,
          suppressErrorRendering: true,
          theme: isHandDrawn ? "neutral" : mermaidTheme,
          securityLevel: "loose",
          fontFamily: isHandDrawn ? "'Architects Daughter', 'Comic Sans MS', cursive, sans-serif" : "Inter, system-ui, sans-serif",
          look: isHandDrawn ? "handDrawn" : "classic",
          flowchart: { curve: isHandDrawn ? "basis" : "linear" },
        });
        mermaid.parseError = () => { };

        const id = `mermaid-svg-${Math.random().toString(36).substring(2, 9)}`;
        const { svg } = await mermaid.render(id, cleanedChart);
        cleanupMermaidErrorDOM();
        if (isMounted) {
          setSvgContent(svg);
          return;
        }
      } catch (err) {
        console.warn("First Mermaid render attempt failed, retrying with classic mode...", err);
        cleanupMermaidErrorDOM();
      }

      // 2nd Attempt: Standard Classic Mode (Foolproof Retry)
      try {
        mermaid.initialize({
          startOnLoad: false,
          suppressErrorRendering: true,
          theme: "neutral",
          securityLevel: "loose",
          look: "classic",
          flowchart: { curve: "linear" },
        });

        const retryId = `mermaid-retry-${Math.random().toString(36).substring(2, 9)}`;
        const { svg } = await mermaid.render(retryId, cleanedChart);
        cleanupMermaidErrorDOM();
        if (isMounted) {
          setSvgContent(svg);
          return;
        }
      } catch (retryErr) {
        console.warn("Second Mermaid render attempt failed. Falling back to Interactive Node Graph.", retryErr);
        cleanupMermaidErrorDOM();
        if (isMounted) {
          setRenderError(true);
          setViewMode("flowchart"); // Auto switch to Interactive ReactFlow Graph!
        }
      }
    };

    renderDiagram();
    return () => {
      isMounted = false;
      cleanupMermaidErrorDOM();
    };
  }, [cleanedChart, mermaidTheme]);

  const liveEditorUrl = useMemo(() => {
    try {
      const state = {
        code: cleanedChart,
        mermaid: { theme: mermaidTheme === "hand-drawn" ? "default" : mermaidTheme, look: mermaidTheme === "hand-drawn" ? "handDrawn" : "classic" },
      };
      const json = JSON.stringify(state);
      const base64 = btoa(encodeURIComponent(json).replace(/%([0-9A-F]{2})/g, (_, p1) => String.fromCharCode(parseInt(p1, 16))));
      return `https://mermaid.live/edit#base64:${base64}`;
    } catch {
      return "https://mermaid.live";
    }
  }, [cleanedChart, mermaidTheme]);

  const handleDownloadSvg = () => {
    if (!svgContent) return;
    const blob = new Blob([svgContent], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `diagram-${kind}.svg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <section className="panel overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 px-5 py-4 bg-slate-50/50">
        <div className="flex items-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-indigo-50 text-indigo-600 shadow-sm">
            <Icon size={20} />
          </span>
          <div>
            <h2 className="font-bold text-slate-800 text-base">{title}</h2>
            <p className="text-xs text-slate-500">Interactive System Architecture Canvas.</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Theme Selector */}
          <div className="flex items-center gap-1.5 bg-slate-100 rounded-lg p-1 text-xs font-medium text-slate-600">
            <Palette size={13} className="text-slate-400 ml-1" />
            <select
              value={mermaidTheme}
              onChange={(e) => setMermaidTheme(e.target.value as MermaidTheme)}
              className="bg-transparent border-0 font-semibold focus:ring-0 cursor-pointer text-slate-700 pr-1 py-0.5"
            >
              <option value="hand-drawn">✏️ Sketch (Hand-drawn)</option>
              <option value="neutral">🎨 Clean Neutral</option>
              <option value="dark">🌙 Dark Theme</option>
              <option value="forest">🌲 Forest Theme</option>
            </select>
          </div>

          {/* View Mode Toggle Buttons */}
          <div className="flex items-center rounded-lg bg-slate-100 p-1 text-xs font-medium text-slate-600">
            <button
              onClick={() => setViewMode("mermaid")}
              className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 transition ${viewMode === "mermaid" ? "bg-white text-indigo-600 shadow-sm font-semibold" : "hover:text-slate-900"
                }`}
            >
              <Image size={14} />
              <span>Diagram</span>
            </button>

            <button
              onClick={() => setViewMode("flowchart")}
              className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 transition ${viewMode === "flowchart" ? "bg-white text-indigo-600 shadow-sm font-semibold" : "hover:text-slate-900"
                }`}
            >
              <Layout size={14} />
              <span>Graph</span>
            </button>

            <button
              onClick={() => setViewMode("raw")}
              className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 transition ${viewMode === "raw" ? "bg-white text-indigo-600 shadow-sm font-semibold" : "hover:text-slate-900"
                }`}
            >
              <Code size={14} />
              <span>Code</span>
            </button>
          </div>

          {/* Export SVG button */}
          {svgContent && (
            <button
              onClick={handleDownloadSvg}
              className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 transition shadow-sm"
              title="Download SVG Diagram"
            >
              <Download size={13} />
              <span>SVG</span>
            </button>
          )}

          {/* Open in Mermaid Live Editor Button */}
          <a
            href={liveEditorUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700 transition shadow-sm"
            title="Open & Edit in Official Mermaid Live Editor"
          >
            <span>Open in Mermaid Live</span>
            <ExternalLink size={13} />
          </a>
        </div>
      </div>

      {/* Main View Area */}
      <div className={`min-h-[520px] w-full ${mermaidTheme === "dark" ? "bg-slate-950 text-white" : "bg-slate-50/30"}`}>
        {viewMode === "mermaid" && (
          <div className="flex min-h-[520px] w-full items-center justify-center p-6 overflow-auto">
            {svgContent ? (
              <div
                ref={containerRef}
                className="mermaid-svg-container max-w-full overflow-auto flex justify-center [&_svg]:max-w-full [&_svg]:h-auto [&_svg]:rounded-lg shadow-sm"
                dangerouslySetInnerHTML={{ __html: svgContent }}
              />
            ) : renderError ? (
              <div className="flex flex-col items-center justify-center text-center p-8 max-w-lg">
                <div className="rounded-xl bg-amber-50 border border-amber-200 p-6 text-amber-900 text-sm">
                  <p className="font-semibold mb-1">Interactive Graph Mode Active</p>
                  <p className="text-xs text-amber-700 mb-3">Viewing diagram using interactive node layout below.</p>
                  <button
                    onClick={() => setViewMode("flowchart")}
                    className="px-4 py-1.5 bg-indigo-600 text-white font-medium text-xs rounded-md shadow-sm hover:bg-indigo-700"
                  >
                    View Interactive Graph
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-slate-400 text-sm">
                <RefreshCw size={18} className="animate-spin text-indigo-500" />
                <span>Rendering System Design Diagram...</span>
              </div>
            )}
          </div>
        )}

        {viewMode === "flowchart" && (
          <div className="h-[560px] bg-[linear-gradient(135deg,#f8faff,#f1f5ff)]">
            <ReactFlow nodes={graph.nodes} edges={graph.edges} fitView minZoom={0.25} maxZoom={1.5} proOptions={{ hideAttribution: true }}>
              <Background color="#cbd5e1" gap={20} size={1} />
              <MiniMap nodeColor="#818cf8" maskColor="rgba(248,250,252,.7)" />
              <Controls showInteractive={false} />
            </ReactFlow>
          </div>
        )}

        {viewMode === "raw" && (
          <div className="p-6">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Mermaid Source Code</span>
              <a
                href={liveEditorUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-indigo-600 hover:underline flex items-center gap-1 font-medium"
              >
                Edit on Mermaid Live <ExternalLink size={12} />
              </a>
            </div>
            <pre className="max-h-[460px] overflow-auto rounded-xl bg-slate-950 p-5 text-xs font-mono leading-6 text-slate-200 border border-slate-800 shadow-inner">
              {cleanedChart}
            </pre>
          </div>
        )}
      </div>

      {/* Footer info */}
      <div className="border-t border-slate-100 px-5 py-3 text-xs text-slate-500 flex items-center justify-between bg-slate-50/50">
        <span>Theme: <strong className="font-semibold text-slate-700 capitalize">{mermaidTheme}</strong></span>
        <a
          href={liveEditorUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-indigo-600 hover:text-indigo-700 font-medium inline-flex items-center gap-1"
        >
          Open in Mermaid Live Editor <ExternalLink size={12} />
        </a>
      </div>
    </section>
  );
}
