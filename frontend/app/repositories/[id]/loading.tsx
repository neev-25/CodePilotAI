export default function RepositoryLoading() {
  return <div className="mx-auto max-w-6xl animate-pulse space-y-6"><div className="h-9 w-64 rounded-lg bg-slate-200"/><div className="h-5 w-96 max-w-full rounded bg-slate-100"/><div className="grid gap-4 sm:grid-cols-4">{Array.from({ length: 4 }).map((_, index) => <div key={index} className="h-28 rounded-2xl bg-white"/>)}</div><div className="h-72 rounded-2xl bg-white"/></div>;
}
