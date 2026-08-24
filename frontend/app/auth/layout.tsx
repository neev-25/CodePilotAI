"use client";

// Auth layout: transparent passthrough — the flip-card page owns its full-screen layout
export default function AuthLayout({ children }: { children: React.ReactNode }) {
    return <>{children}</>;
}
