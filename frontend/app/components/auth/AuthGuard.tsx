"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/app/contexts/AuthContext";

interface Props {
    children: React.ReactNode;
}

export default function AuthGuard({ children }: Props) {
    const { user, loading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!loading && !user) {
            router.replace("/landing");
        }
    }, [loading, user, router]);

    // While restoring session, show a minimal loading state
    if (loading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-[var(--bg)]">
                <div className="flex flex-col items-center gap-3">
                    <span className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-500/30 border-t-indigo-500" />
                    <p className="text-sm text-[var(--fg-muted)]">Loading…</p>
                </div>
            </div>
        );
    }

    if (!user) return null;

    return <>{children}</>;
}
