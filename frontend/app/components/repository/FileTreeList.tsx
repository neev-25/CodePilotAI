import Link from "next/link";
import { FileTreeNode } from "@/app/lib/repository";

interface Props {
  repoId: string;
  nodes: FileTreeNode[];
  prefix?: string;
  selectedFile?: string | null;
}

function buildPath(prefix: string, name: string) {
  return prefix ? `${prefix}/${name}` : name;
}

export default function FileTreeList({ repoId, nodes, prefix = "", selectedFile = null }: Props) {
  return (
    <div className="space-y-1">
      {nodes.map((node) => {
        const path = buildPath(prefix, node.name);

        if (node.type === "directory") {
          return (
            <div key={path} className="ml-0">
              <div className="font-semibold text-gray-700 py-2 flex items-center gap-2">
                <span className="text-blue-500">📁</span>
                {node.name}
              </div>
              {node.children && node.children.length > 0 && (
                <div className="ml-6 border-l border-gray-200 pl-4">
                  <FileTreeList
                    repoId={repoId}
                    nodes={node.children}
                    prefix={path}
                    selectedFile={selectedFile}
                  />
                </div>
              )}
            </div>
          );
        }

        const isSelected = selectedFile === path;

        return (
          <Link
            key={path}
            href={`/repositories/${repoId}/files?file=${encodeURIComponent(path)}`}
            className={`block rounded-lg px-3 py-2 text-sm transition-colors ${isSelected ? "bg-indigo-50 text-indigo-700 font-medium" : "text-gray-600 hover:bg-gray-100"
              }`}
          >
            <div className="flex items-center gap-2 truncate">
              <span className={isSelected ? "text-indigo-500" : "text-gray-400"}>📄</span>
              <span className="truncate">{node.name}</span>
            </div>
          </Link>
        );
      })}
    </div>
  );
}
