"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

// Register is now integrated into the flip-card login page
export default function RegisterRedirect() {
    const router = useRouter();
    useEffect(() => {
        router.replace("/auth/login");
    }, [router]);
    return null;
}
