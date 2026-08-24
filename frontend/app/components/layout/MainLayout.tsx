"use client";

import Sidebar from "./Sidebar";
import Header from "./Header";
import AuthGuard from "../auth/AuthGuard";
import { useState } from "react";

interface Props {
    children: React.ReactNode;
}

export default function MainLayout({ children }: Props) {
    const [mobileNavOpen, setMobileNavOpen] = useState(false);

    return (
        <AuthGuard>
            <div className="flex min-h-screen" style={{ background: "var(--bg)" }}>
                <Sidebar open={mobileNavOpen} onClose={() => setMobileNavOpen(false)} />
                <div className="flex min-w-0 flex-1 flex-col">
                    <Header onOpenMenu={() => setMobileNavOpen(true)} />
                    <main className="app-surface min-h-[calc(100vh-4.5rem)] flex-1 overflow-auto p-4 sm:p-6 lg:p-8">
                        {children}
                    </main>
                </div>
            </div>
        </AuthGuard>
    );
}
