"use client";

import ErrorCard from "@/app/components/repository/ErrorCard";

export default function Error() {
  return (
    <ErrorCard
      title="Failed to Load Review"
      message="The repository may not be indexed yet. Please try again."
    />
  );
}
