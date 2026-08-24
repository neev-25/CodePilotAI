"use client";

export default function Error() {
  return (
    <div className="max-w-6xl mx-auto p-8">
      <div className="border border-red-200 rounded-xl bg-red-50 p-8">
        <h1 className="text-2xl font-bold text-red-600">Failed to Analyze Architecture</h1>
        <p className="mt-3 text-gray-600">Please try again.</p>
      </div>
    </div>
  );
}
