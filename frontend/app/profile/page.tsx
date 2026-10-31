"use client";

import { useAuth } from "@/app/contexts/AuthContext";
import { User, LogOut, Loader2, Mail, Clock, KeyRound, CheckCircle2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import axios from "axios";
import MainLayout from "../components/layout/MainLayout";
import { changePassword } from "../lib/authApi";

export default function ProfilePage() {
    const { user, logout, loading } = useAuth();
    const router = useRouter();
    const [currentPassword, setCurrentPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [passwordError, setPasswordError] = useState("");
    const [passwordSaved, setPasswordSaved] = useState(false);
    const [savingPassword, setSavingPassword] = useState(false);

    if (loading) {
        return (
            <MainLayout>
                <div className="flex h-64 items-center justify-center">
                    <Loader2 size={32} className="animate-spin text-indigo-500" />
                </div>
            </MainLayout>
        );
    }

    if (!user) {
        return null;
    }

    const handleLogout = () => {
        logout();
        router.push("/auth/login");
    };

    async function handleChangePassword(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        setPasswordError("");
        setPasswordSaved(false);
        if (newPassword !== confirmPassword) {
            setPasswordError("The new passwords do not match.");
            return;
        }

        setSavingPassword(true);
        try {
            await changePassword(currentPassword, newPassword);
            setCurrentPassword("");
            setNewPassword("");
            setConfirmPassword("");
            setPasswordSaved(true);
        } catch (error) {
            const detail = axios.isAxiosError<{ detail?: string }>(error)
                ? error.response?.data?.detail
                : undefined;
            setPasswordError(detail ?? "Password could not be changed. Please try again.");
        } finally {
            setSavingPassword(false);
        }
    }

    return (
        <MainLayout>
        <div className="mx-auto max-w-4xl space-y-6 pt-2">
            <div className="flex items-center justify-between border-b border-[var(--border)] pb-4">
                <div>
                    <h1 className="text-2xl font-bold">Profile</h1>
                    <p className="mt-1 text-sm text-[var(--fg-muted)]">
                        Manage your account settings and preferences.
                    </p>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                {/* Profile Card */}
                <div className="panel rounded-xl p-6">
                    <div className="flex items-center gap-4 border-b border-[var(--border)] pb-4">
                        <div className="grid h-16 w-16 place-items-center rounded-full bg-indigo-500/10 text-indigo-500">
                            <User size={32} />
                        </div>
                        <div>
                            <h2 className="text-xl font-semibold">{user.name}</h2>
                            <p className="text-sm font-medium text-[var(--fg-muted)] flex items-center gap-2 mt-1">
                                <Mail size={14} /> {user.email}
                            </p>
                        </div>
                    </div>

                    <div className="mt-6 space-y-4">
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-[var(--fg-muted)] flex items-center gap-2">
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

                <div className="panel rounded-xl p-6">
                    <div className="mb-5 flex items-center gap-2">
                        <KeyRound size={18} className="text-indigo-500" />
                        <h3 className="text-lg font-semibold">Change password</h3>
                    </div>
                    <form onSubmit={handleChangePassword} className="space-y-4">
                        <label className="block text-sm font-medium">
                            Current password
                            <input
                                className="input-base mt-1.5"
                                type="password"
                                autoComplete="current-password"
                                value={currentPassword}
                                onChange={(event) => setCurrentPassword(event.target.value)}
                                required
                            />
                        </label>
                        <label className="block text-sm font-medium">
                            New password
                            <input
                                className="input-base mt-1.5"
                                type="password"
                                autoComplete="new-password"
                                value={newPassword}
                                onChange={(event) => setNewPassword(event.target.value)}
                                minLength={8}
                                required
                            />
                        </label>
                        <label className="block text-sm font-medium">
                            Confirm new password
                            <input
                                className="input-base mt-1.5"
                                type="password"
                                autoComplete="new-password"
                                value={confirmPassword}
                                onChange={(event) => setConfirmPassword(event.target.value)}
                                minLength={8}
                                required
                            />
                        </label>
                        {passwordError && <p role="alert" className="text-sm text-rose-500">{passwordError}</p>}
                        {passwordSaved && (
                            <p role="status" className="flex items-center gap-2 text-sm text-emerald-500">
                                <CheckCircle2 size={16} /> Password changed successfully.
                            </p>
                        )}
                        <button
                            type="submit"
                            disabled={savingPassword}
                            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:opacity-60"
                        >
                            {savingPassword ? "Changing..." : "Change password"}
                        </button>
                    </form>
                </div>
            </div>
        </div>
        </MainLayout>
    );
}
