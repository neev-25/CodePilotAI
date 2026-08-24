"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/app/contexts/AuthContext";

// Landing page is replaced by the flip-card auth page
export default function LandingRedirect() {
    const { user, loading } = useAuth();
    const router = useRouter();
    useEffect(() => {
        if (!loading) {
            router.replace(user ? "/" : "/auth/login");
        }
    }, [loading, user, router]);
    return null;
}
