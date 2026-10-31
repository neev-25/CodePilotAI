"use client";

import Link from "next/link";
import MainLayout from "../components/layout/MainLayout";
import { useTheme } from "../contexts/ThemeContext";
import { useAuth } from "../contexts/AuthContext";
import { LockKeyhole, Moon, Sun, UserRound } from "lucide-react";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const { user } = useAuth();

  return (
    <MainLayout>
      <div className="mx-auto max-w-3xl space-y-6 pt-2">
        <div>
          <h1 className="text-3xl font-bold" style={{ color: "var(--fg)" }}>Settings</h1>
          <p className="mt-1 text-sm" style={{ color: "var(--fg-muted)" }}>
            Personalize your workspace and manage your account.
          </p>
        </div>

        <section className="panel overflow-hidden rounded-2xl">
          <div className="border-b px-6 py-4" style={{ borderColor: "var(--border)" }}>
            <h2 className="font-semibold" style={{ color: "var(--fg)" }}>Appearance</h2>
            <p className="mt-1 text-sm" style={{ color: "var(--fg-muted)" }}>
              Choose a theme for this browser.
            </p>
          </div>
          <div className="grid gap-3 p-6 sm:grid-cols-2">
            {([
              { value: "light", label: "Light", Icon: Sun },
              { value: "dark", label: "Dark", Icon: Moon },
            ] as const).map(({ value, label, Icon }) => (
              <button
                key={value}
                type="button"
                aria-pressed={theme === value}
                onClick={() => setTheme(value)}
                className="flex items-center gap-3 rounded-xl border p-4 text-left transition"
                style={{
                  borderColor: theme === value ? "#6366f1" : "var(--border)",
                  background: theme === value ? "rgba(99, 102, 241, 0.1)" : "var(--bg)",
                  color: "var(--fg)",
                }}
              >
                <Icon size={20} className="text-indigo-500" />
                <span className="font-medium">{label} mode</span>
                <span className="ml-auto text-xs" style={{ color: "var(--fg-muted)" }}>
                  {theme === value ? "Selected" : "Select"}
                </span>
              </button>
            ))}
          </div>
        </section>

        <section className="panel flex flex-col gap-4 rounded-2xl p-6 sm:flex-row sm:items-center">
          <div className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-indigo-500/10 text-indigo-500">
            <LockKeyhole size={21} />
          </div>
          <div className="min-w-0 flex-1">
            <h2 className="font-semibold" style={{ color: "var(--fg)" }}>Account security</h2>
            <p className="mt-1 text-sm" style={{ color: "var(--fg-muted)" }}>
              {user?.email ?? "Manage your password and profile details."}
            </p>
          </div>
          <Link
            href="/profile"
            className="inline-flex items-center justify-center gap-2 rounded-xl border px-4 py-2 text-sm font-semibold transition hover:border-indigo-400"
            style={{ borderColor: "var(--border)", color: "var(--fg)" }}
          >
            <UserRound size={16} /> Profile
          </Link>
        </section>

        <p className="text-xs leading-5" style={{ color: "var(--fg-muted)" }}>
          Backend and database connections are configured by the workspace environment, not stored in browser settings.
        </p>
      </div>
    </MainLayout>
  );
}
