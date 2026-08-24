"use client";

import { useEffect, useState } from "react";

import MainLayout from "../components/layout/MainLayout";

import RepositoryCard from "../components/repository/RepositoryCard";

import CloneRepository from "../components/repository/CloneRepository";

import {
  getRepositories,
  cloneRepository,
  deleteRepository,
  type Repository,
} from "../lib/repository";
import Link from "next/link";
import { FolderGit2 } from "lucide-react";

export default function RepositoryPage() {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadRepositories() {
    setError("");
    try { setRepositories(await getRepositories()); } catch { setError("We couldn’t reach the CodePilot backend. Start it and refresh this page."); } finally { setIsLoading(false); }
  }

  useEffect(() => {
    void getRepositories()
      .then(setRepositories)
      .catch(() => setError("We couldn’t reach the CodePilot backend. Start it and refresh this page."))
      .finally(() => setIsLoading(false));
  }, []);

  async function handleClone(url: string) {
    if (!url) return;

    await cloneRepository(url); await loadRepositories();
  }

  async function handleDelete(id: number) {
    await deleteRepository(id); await loadRepositories();
  }

  return (
    <MainLayout>
      <div className="mx-auto max-w-6xl space-y-8">
        <CloneRepository onClone={handleClone} />

        <div>
          <div className="mb-5 flex items-end justify-between"><div><p className="eyebrow">Your workspaces</p><h2 className="mt-1 text-2xl font-bold text-slate-800">Repositories</h2></div>{repositories.length > 0 && <span className="rounded-full bg-indigo-50 px-3 py-1 text-sm font-semibold text-indigo-700">{repositories.length} connected</span>}</div>

          <div className="space-y-4">
            {isLoading && <div className="panel animate-pulse rounded-2xl p-6 text-sm text-slate-400">Loading your repositories…</div>}
            {error && <div role="alert" className="rounded-2xl border border-rose-200 bg-rose-50 p-5 text-sm text-rose-700">{error}</div>}
            {!isLoading && !error && repositories.length === 0 && <div className="panel rounded-2xl py-14 text-center"><span className="mx-auto grid h-12 w-12 place-items-center rounded-xl bg-indigo-50 text-indigo-600"><FolderGit2 size={24}/></span><h3 className="mt-4 font-bold text-slate-800">No repositories connected</h3><p className="mx-auto mt-2 max-w-sm text-sm leading-6 text-slate-500">Connect a GitHub repository above to unlock AI-powered analysis, review, and documentation.</p></div>}
            {repositories.map((repo) => {
              return (
                <Link key={repo.id} href={`/repositories/${repo.id}`}>
                  <RepositoryCard
                    repository={repo}
                    onDelete={() => handleDelete(repo.id)}
                  />
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
