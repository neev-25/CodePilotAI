export default function Loading() {
  return (
    <div className="max-w-6xl mx-auto p-8">
      <div className="animate-pulse">
        <div className="h-10 bg-gray-200 rounded w-80 mb-8" />

        <div className="space-y-4">
          <div className="h-5 bg-gray-200 rounded" />

          <div className="h-5 bg-gray-200 rounded" />

          <div className="h-5 bg-gray-200 rounded" />

          <div className="h-5 bg-gray-200 rounded" />
        </div>
      </div>
    </div>
  );
}
