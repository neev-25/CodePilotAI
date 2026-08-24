export default function SummarySkeleton() {
  return (
    <div className="border rounded-xl p-6 animate-pulse">
      <div className="h-6 w-52 bg-gray-200 rounded mb-5" />

      <div className="space-y-3">
        <div className="h-4 bg-gray-200 rounded" />

        <div className="h-4 bg-gray-200 rounded" />

        <div className="h-4 bg-gray-200 rounded" />

        <div className="h-4 w-3/4 bg-gray-200 rounded" />
      </div>
    </div>
  );
}
