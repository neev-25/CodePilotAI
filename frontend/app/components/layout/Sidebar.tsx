"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Sparkles, X } from "lucide-react";
import { navigation } from "./navigation";

interface Props { open: boolean; onClose: () => void; }

export default function Sidebar({ open, onClose }: Props) {
  const pathname = usePathname();

  return (
    <>
      {open && (
        <button
          aria-label="Close navigation"
          onClick={onClose}
          className="fixed inset-0 z-30 bg-slate-950/45 lg:hidden"
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex h-screen w-72 flex-col shadow-2xl transition-transform lg:sticky lg:top-0 lg:translate-x-0 ${open ? "translate-x-0" : "-translate-x-full"}`}
        style={{ background: "#101827", color: "white" }}
      >
        {/* Logo */}
        <div className="flex items-start justify-between border-b border-white/10 px-6 py-6">
          <div>
            <div className="flex items-center gap-2 text-xl font-bold">
              <span className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-indigo-400 to-cyan-400 text-slate-950">
                <Sparkles size={17} />
              </span>
              CodePilot
            </div>
            <p className="mt-2 text-xs font-medium tracking-wide text-slate-400">AI DEVELOPER PLATFORM</p>
          </div>
          <button
            onClick={onClose}
            aria-label="Close navigation"
            className="rounded-lg p-1 text-slate-400 hover:bg-white/10 lg:hidden"
          >
            <X size={20} />
          </button>
        </div>

        {/* Nav items */}
        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-5">
          {navigation.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onClose}
                className={`flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all ${active
                    ? "bg-gradient-to-r from-indigo-500 to-blue-500 text-white shadow-lg shadow-indigo-950/30"
                    : "text-slate-300 hover:bg-white/8 hover:text-white"
                  }`}
              >
                <Icon size={19} />
                <span>{item.title}</span>
              </Link>
            );
          })}
        </nav>

        {/* Status bar */}
        <div className="m-3 rounded-xl border border-white/10 bg-white/5 p-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-emerald-300">
            <span className="h-2 w-2 rounded-full bg-emerald-400" /> SYSTEMS OPERATIONAL
          </div>
          <div className="mt-2 text-xs leading-5 text-slate-400">
            AI insights are ready whenever your repository is indexed.
          </div>
        </div>
      </aside>
    </>
  );
}
