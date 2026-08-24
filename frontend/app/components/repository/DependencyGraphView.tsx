"use client";

import { useCallback, useMemo } from "react";
import dagre from "dagre";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  Position,
} from "reactflow";
import "reactflow/dist/style.css";
import { DependencyGraph } from "@/app/lib/repository";

interface Props {
  graph: DependencyGraph;
}

export default function DependencyGraphView({ graph }: Props) {
  const { nodes, edges } = useMemo(() => {
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));
    dagreGraph.setGraph({ rankdir: 'LR', nodesep: 50, ranksep: 100 });

    const flowNodes: Node[] = graph.nodes.map((n) => ({
      id: n.path,
      data: { label: n.path.split("/").pop() ?? n.path },
      position: { x: 0, y: 0 },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      style: {
        background: "#eff6ff",
        border: "1px solid #3b82f6",
        borderRadius: "8px",
        padding: "8px",
        fontSize: "12px",
        maxWidth: "200px",
      },
    }));

    const flowEdges: Edge[] = graph.edges.map((e, i) => ({
      id: `e-${i}`,
      source: e.from_file,
      target: e.to_file,
      animated: true,
      style: { stroke: "#6b7280", strokeWidth: 2 },
    }));

    flowNodes.forEach((node) => {
      dagreGraph.setNode(node.id, { width: 200, height: 40 });
    });

    flowEdges.forEach((edge) => {
      dagreGraph.setEdge(edge.source, edge.target);
    });

    dagre.layout(dagreGraph);

    flowNodes.forEach((node) => {
      const nodeWithPosition = dagreGraph.node(node.id);
      node.position = {
        x: nodeWithPosition.x - 100,
        y: nodeWithPosition.y - 20,
      };
    });

    return { nodes: flowNodes, edges: flowEdges };
  }, [graph]);

  const onInit = useCallback(() => { }, []);

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
