"use client";

import Link from "next/link";
import { ArrowRight, Bot, FileSearch, GitBranch, ShieldCheck, Sparkles, Moon, Sun } from "lucide-react";
import { useTheme } from "@/app/contexts/ThemeContext";

const workflows = [
  { title: "Repository intelligence", description: "Explore code, dependencies, docs, and diagrams in one workspace.", href: "/repositories", icon: GitBranch },
  { title: "Quality & health", description: "Surface complexity, technical debt, and actions that matter first.", href: "/analysis", icon: FileSearch },
  { title: "Security posture", description: "Review risks and reliability concerns before they reach production.", href: "/security", icon: ShieldCheck },
];

export default function HomePage() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="mx-auto max-w-7xl space-y-7">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-3xl bg-[#101827] px-6 py-10 text-white shadow-xl shadow-slate-300/40 sm:px-10 sm:py-14">
        <div className="absolute -right-16 -top-24 h-72 w-72 rounded-full bg-indigo-500/30 blur-3xl" />
        <div className="absolute bottom-0 right-1/4 h-44 w-44 rounded-full bg-cyan-400/15 blur-3xl" />
        <div className="relative max-w-3xl">
          <p className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-semibold text-indigo-100">
            <Sparkles size={14} /> YOUR AI ENGINEERING WORKSPACE
          </p>
          <h1 className="mt-5 text-4xl font-bold tracking-tight sm:text-5xl">
            Ship with a clearer view of your codebase.
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-300 sm:text-lg">
            CodePilot turns a repository into fast, reusable engineering context—from architecture to security and the next best improvement.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/repositories" className="inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-bold text-slate-900 shadow-lg transition hover:bg-indigo-50">
              Connect a repository <ArrowRight size={17} />
            </Link>
            <Link href="/analysis" className="rounded-xl border border-white/20 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10">
              Explore analysis
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="grid gap-4 sm:grid-cols-3">
        {[
          ["AI tools", "19", "Focused workflows"],
          ["Coverage", "End-to-end", "From clone to ship"],
          ["Saved context", "Reusable", "Across your team"],
        ].map(([label, value, detail]) => (
          <div key={label} className="panel rounded-2xl p-5">
            <p className="eyebrow">{label}</p>
            <p className="mt-2 text-2xl font-bold" style={{ color: "var(--fg)" }}>{value}</p>
            <p className="mt-1 text-sm" style={{ color: "var(--fg-muted)" }}>{detail}</p>
          </div>
        ))}
      </section>

      {/* Workflows */}
      <section>
        <div className="mb-4 flex items-end justify-between">
          <div>
            <p className="eyebrow">Start here</p>
            <h2 className="mt-1 text-2xl font-bold" style={{ color: "var(--fg)" }}>Pick a workflow</h2>
          </div>
          <Link className="hidden text-sm font-semibold text-indigo-600 hover:text-indigo-700 sm:block" href="/repositories">
            View repositories →
          </Link>
        </div>
        <div className="grid gap-4 lg:grid-cols-3">
          {workflows.map(({ title, description, href, icon: Icon }) => (
            <Link
              key={title}
              href={href}
              className="panel group rounded-2xl p-6 transition duration-200 hover:-translate-y-1 hover:border-indigo-200 hover:shadow-lg"
            >
              <span className="grid h-11 w-11 place-items-center rounded-xl bg-indigo-50 text-indigo-600">
                <Icon size={21} />
              </span>
              <h3 className="mt-5 text-lg font-bold" style={{ color: "var(--fg)" }}>{title}</h3>
              <p className="mt-2 text-sm leading-6" style={{ color: "var(--fg-muted)" }}>{description}</p>
              <span className="mt-5 inline-flex items-center gap-1 text-sm font-semibold text-indigo-600">
                Open workflow <ArrowRight className="transition group-hover:translate-x-1" size={16} />
              </span>
            </Link>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="panel flex flex-col items-start justify-between gap-5 rounded-2xl p-6 sm:flex-row sm:items-center">
        <div className="flex gap-4">
          <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl" style={{ background: "var(--border)", color: "var(--fg)" }}>
            <Bot size={22} />
          </span>
          <div>
            <h2 className="font-bold" style={{ color: "var(--fg)" }}>Bring your first repository to life</h2>
            <p className="mt-1 text-sm" style={{ color: "var(--fg-muted)" }}>Clone, index, then use every AI workflow from one shared context.</p>
          </div>
        </div>
        <Link href="/repositories" className="whitespace-nowrap rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700">
          Manage repositories
        </Link>
      </section>
    </div>
  );
}
