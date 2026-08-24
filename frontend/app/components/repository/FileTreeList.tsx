import Link from "next/link";
import { FileTreeNode } from "@/app/lib/repository";

interface Props {
  repoId: string;
  nodes: FileTreeNode[];
  prefix?: string;
}

function buildPath(prefix: string, name: string) {
  return prefix ? `${prefix}/${name}` : name;
}

export default function FileTreeList({ repoId, nodes, prefix = "" }: Props) {
  return (
    <div className="space-y-2">
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
                  />
                </div>
              )}
            </div>
          );
        }

        return (
          <div
            key={path}
            className="border rounded-xl p-4 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 bg-white"
          >
            <div className="min-w-0">
              <h2 className="font-semibold flex items-center gap-2">
                <span className="text-gray-400">📄</span>
                {node.name}
              </h2>
              <p className="text-gray-500 text-sm truncate">{path}</p>
            </div>
            <div className="flex flex-wrap gap-2 shrink-0">
              <Link
                href={`/repositories/${repoId}/explain?file=${encodeURIComponent(path)}`}
                className="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-blue-700"
              >
                Explain
              </Link>
              <Link
                href={`/repositories/${repoId}/documentation?file=${encodeURIComponent(path)}`}
                className="bg-green-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-green-700"
              >
                Documentation
              </Link>
              <Link
                href={`/repositories/${repoId}/function-explain?file=${encodeURIComponent(path)}`}
                className="bg-purple-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-purple-700"
              >
                Function
              </Link>
              <Link
                href={`/repositories/${repoId}/tests?file=${encodeURIComponent(path)}`}
                className="bg-orange-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-orange-700"
              >
                Tests
              </Link>
            </div>
          </div>
        );
      })}
    </div>
  );
}
