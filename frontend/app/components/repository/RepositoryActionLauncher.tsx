"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { getRepositories, type Repository } from "@/app/lib/repository";

type Action = {
  label: string;
  href: string;
  description: string;
};

type Props = {
  title: string;
  description: string;
  actions: Action[];
};

export default function RepositoryActionLauncher({ title, description, actions }: Props) {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [repositoryId, setRepositoryId] = useState<number | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    getRepositories()
      .then((items) => {
        setRepositories(items);
        setRepositoryId(items[0]?.id ?? null);
      })
      .catch(() => setError(true));
  }, []);

  return (
    <section className="max-w-4xl space-y-6">
      <div>
        <h1 className="text-4xl font-bold tracking-tight">{title}</h1>
        <p className="mt-3 text-gray-600">{description}</p>
      </div>

      {error ? (
        <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-red-700">
          The repository list could not be loaded. Confirm that the backend is running.
        </div>
      ) : repositories.length === 0 ? (
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold">Start with a repository</h2>
          <p className="mt-2 text-gray-600">Clone and index a Git repository before using this tool.</p>
          <Link href="/repositories" className="mt-5 inline-flex rounded-lg bg-blue-600 px-5 py-2.5 font-medium text-white hover:bg-blue-700">
            Add a repository
          </Link>
        </div>
      ) : (
        <>
          <label className="block max-w-xl text-sm font-medium text-gray-700">
            Repository
            <select
              value={repositoryId ?? ""}
              onChange={(event) => setRepositoryId(Number(event.target.value))}
              className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-base shadow-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            >
              {repositories.map((repository) => (
                <option value={repository.id} key={repository.id}>{repository.name}</option>
              ))}
            </select>
          </label>

          <div className="grid gap-4 sm:grid-cols-2">
            {repositoryId && actions.map((action) => (
              <Link
                href={action.href.replace(":id", String(repositoryId))}
                key={action.label}
                className="rounded-xl border bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-300 hover:shadow-md"
              >
                <h2 className="font-semibold text-gray-900">{action.label}</h2>
                <p className="mt-2 text-sm leading-6 text-gray-600">{action.description}</p>
              </Link>
            ))}
          </div>
        </>
      )}
    </section>
  );
}
