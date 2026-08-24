interface Props {
  title?: string;
}

export default function LoadingSkeleton({ title }: Props) {
  return (
    <div className="max-w-6xl mx-auto p-8">
      {title && (
        <div className="animate-pulse h-10 bg-gray-200 rounded w-80 mb-8" />
      )}
      <div className="animate-pulse space-y-4">
        <div className="h-32 bg-gray-200 rounded-xl" />
        <div className="h-5 bg-gray-200 rounded w-full" />
        <div className="h-5 bg-gray-200 rounded w-5/6" />
        <div className="h-5 bg-gray-200 rounded w-4/6" />
        <div className="h-48 bg-gray-200 rounded-xl mt-6" />
      </div>
    </div>
  );
}
