"use client";

import { useAuth } from "@/app/contexts/AuthContext";
import { User, LogOut, Loader2, Mail, Clock } from "lucide-react";
import { useRouter } from "next/navigation";

export default function ProfilePage() {
    const { user, logout, loading } = useAuth();
    const router = useRouter();

    if (loading) {
        return (
            <div className="flex h-64 items-center justify-center">
                <Loader2 size={32} className="animate-spin text-indigo-500" />
            </div>
        );
    }

    if (!user) {
        return null;
    }

    const handleLogout = () => {
        logout();
        router.push("/auth/login");
    };

    return (
        <div className="mx-auto max-w-4xl space-y-6">
            <div className="flex items-center justify-between border-b border-[var(--border)] pb-4">
                <div>
                    <h1 className="text-2xl font-bold">Profile</h1>
                    <p className="mt-1 text-sm text-[var(--muted)]">
                        Manage your account settings and preferences.
                    </p>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                {/* Profile Card */}
                <div className="rounded-xl border border-[var(--border)] p-6 shadow-sm bg-[var(--surface-50)]">
                    <div className="flex items-center gap-4 border-b border-[var(--border)] pb-4">
                        <div className="grid h-16 w-16 place-items-center rounded-full bg-indigo-500/10 text-indigo-500">
                            <User size={32} />
                        </div>
                        <div>
                            <h2 className="text-xl font-semibold">{user.name}</h2>
                            <p className="text-sm font-medium text-[var(--muted)] flex items-center gap-2 mt-1">
                                <Mail size={14} /> {user.email}
                            </p>
                        </div>
                    </div>

                    <div className="mt-6 space-y-4">
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-[var(--muted)] flex items-center gap-2">
                                <Clock size={16} /> Member Since
                            </span>
                            <span className="text-sm font-semibold">
                                {new Date(user.created_at).toLocaleDateString()}
                            </span>
                        </div>
                    </div>

                    <div className="mt-8 border-t border-[var(--border)] pt-4">
                        <button
                            onClick={handleLogout}
                            className="flex items-center gap-2 rounded-lg bg-red-500/10 px-4 py-2 text-sm font-medium text-red-500 hover:bg-red-500/20 transition-colors"
                        >
                            <LogOut size={16} />
                            Sign out
                        </button>
                    </div>
                </div>

                {/* Settings Placeholder */}
                <div className="rounded-xl border border-[var(--border)] p-6 shadow-sm bg-[var(--surface-50)]">
                    <h3 className="text-lg font-semibold mb-4">Account Settings</h3>
                    <p className="text-sm text-[var(--muted)] mb-6">
                        More profile settings and organization configuration options will be available soon.
                    </p>
                    <button disabled className="w-full rounded-lg bg-[var(--surface-100)] px-4 py-2 text-sm font-medium text-[var(--muted)] cursor-not-allowed">
                        Change Password
                    </button>
                </div>
            </div>
        </div>
    );
}
