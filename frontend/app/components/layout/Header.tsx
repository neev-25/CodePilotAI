"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Bell, Menu, Moon, Search, Sun, LogOut } from "lucide-react";
import { navigation } from "./navigation";
import { useTheme } from "@/app/contexts/ThemeContext";
import { useAuth } from "@/app/contexts/AuthContext";
import { useRouter } from "next/navigation";

export default function Header({ onOpenMenu }: { onOpenMenu: () => void }) {
  const pathname = usePathname();
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const currentPage = navigation.find((item) => item.href === pathname)?.title ?? "Repository Workspace";

  const { theme, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  const router = useRouter();

  const initials = user?.name
    ? user.name.split(" ").map((n) => n[0]).join("").slice(0, 2).toUpperCase()
    : "AI";

  function handleLogout() {
    logout();
    router.replace("/landing");
  }

  return (
    <header
      className="flex h-[4.5rem] items-center justify-between px-4 backdrop-blur-xl sm:px-6 lg:px-8"
      style={{
        background: "var(--bg-panel)",
        borderBottom: "1px solid var(--border)",
      }}
    >
      {/* Left */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMenu}
          aria-label="Open navigation"
          className="rounded-lg p-2 lg:hidden"
          style={{ color: "var(--fg-muted)" }}
        >
          <Menu size={21} />
        </button>
        <div>
          <p className="hidden text-[10px] font-bold tracking-[.16em] sm:block" style={{ color: "var(--fg-subtle)" }}>
            WORKSPACE
          </p>
          <h2 className="text-lg font-bold sm:text-xl" style={{ color: "var(--fg)" }}>
            {currentPage}
          </h2>
        </div>
      </div>

      {/* Right */}
      <div className="relative flex items-center gap-1">
        {/* Search */}
        <Link
          href="/search"
          aria-label="Open repository search"
          className="rounded-xl p-2.5 transition-colors"
          style={{ color: "var(--fg-muted)" }}
        >
          <Search size={20} />
        </Link>

        {/* Notifications */}
        <button
          type="button"
          aria-label="Show notifications"
          aria-expanded={notificationsOpen}
          onClick={() => { setNotificationsOpen((o) => !o); setUserMenuOpen(false); }}
          className="relative rounded-xl p-2.5 transition-colors"
          style={{ color: "var(--fg-muted)" }}
        >
          <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-indigo-500" />
          <Bell size={20} />
        </button>

        {/* Theme toggle */}
        <button
          type="button"
          aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
          onClick={toggleTheme}
          className="rounded-xl p-2.5 transition-colors"
          style={{ color: "var(--fg-muted)" }}
        >
          {theme === "dark" ? <Sun size={20} /> : <Moon size={20} />}
        </button>

        {/* User avatar + dropdown */}
        <button
          aria-label="User menu"
          onClick={() => { setUserMenuOpen((o) => !o); setNotificationsOpen(false); }}
          className="ml-1 flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 text-xs font-bold text-white shadow-md shadow-indigo-200 hover:brightness-105"
        >
          {initials}
        </button>

        {/* Notifications panel */}
        {notificationsOpen && (
          <div
            className="absolute right-0 top-14 z-20 w-72 rounded-2xl p-4 shadow-xl"
            style={{ background: "var(--bg-panel)", border: "1px solid var(--border)" }}
          >
            <p className="font-semibold" style={{ color: "var(--fg)" }}>Notifications</p>
            <p className="mt-2 text-sm leading-6" style={{ color: "var(--fg-muted)" }}>
              You're all caught up. Analysis results are saved per repository.
            </p>
          </div>
        )}

        {/* User dropdown */}
        {userMenuOpen && (
          <div
            className="absolute right-0 top-14 z-20 w-56 rounded-2xl p-2 shadow-xl"
            style={{ background: "var(--bg-panel)", border: "1px solid var(--border)" }}
          >
            <div className="px-3 py-2">
              <p className="text-sm font-semibold truncate" style={{ color: "var(--fg)" }}>{user?.name}</p>
              <p className="text-xs truncate" style={{ color: "var(--fg-muted)" }}>{user?.email}</p>
            </div>
            <div style={{ borderTop: "1px solid var(--border)", margin: "4px 0" }} />

            <button
              onClick={handleLogout}
              className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-sm transition-colors hover:bg-red-50"
              style={{ color: "#ef4444" }}
            >
              <LogOut size={15} /> Sign out
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
