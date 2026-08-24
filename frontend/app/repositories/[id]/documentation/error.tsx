"use client";

export default function Error() {
  return (
    <div className="max-w-5xl mx-auto p-8">
      <h1 className="text-3xl font-bold text-red-600">
        Failed to Generate Documentation
      </h1>

      <p className="mt-4">Please try again.</p>
    </div>
  );
}
