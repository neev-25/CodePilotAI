"use client";

import { useCallback, useMemo } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
} from "reactflow";
import "reactflow/dist/style.css";
import { DependencyGraph } from "@/app/lib/repository";

interface Props {
  graph: DependencyGraph;
}

export default function DependencyGraphView({ graph }: Props) {
  const { nodes, edges } = useMemo(() => {
    const flowNodes: Node[] = graph.nodes.map((n, i) => ({
      id: n.path,
      data: { label: n.path.split("/").pop() ?? n.path },
      position: {
        x: (i % 5) * 200,
        y: Math.floor(i / 5) * 100,
      },
      style: {
        background: "#eff6ff",
        border: "1px solid #3b82f6",
        borderRadius: "8px",
        padding: "8px",
        fontSize: "12px",
        maxWidth: "180px",
      },
    }));

    const flowEdges: Edge[] = graph.edges.map((e, i) => ({
      id: `e-${i}`,
      source: e.from_file,
      target: e.to_file,
      animated: true,
      style: { stroke: "#6b7280" },
    }));

    return { nodes: flowNodes, edges: flowEdges };
  }, [graph]);

  const onInit = useCallback(() => {}, []);

  if (graph.nodes.length === 0) {
    return (
      <p className="text-gray-500 border rounded-xl p-6 bg-white">
        No dependency nodes found.
      </p>
    );
  }

  return (
    <div className="border rounded-xl bg-white h-[600px]">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onInit={onInit}
        fitView
        attributionPosition="bottom-left"
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}
