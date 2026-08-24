"use client";

import { useState, useEffect } from "react";
import MainLayout from "../components/layout/MainLayout";
import { Save, CheckCircle, Server, Key, Info, ExternalLink, RefreshCw } from "lucide-react";

export default function SettingsPage() {
  const [endpoint, setEndpoint] = useState("http://127.0.0.1:8000");
  const [apiKey, setApiKey] = useState("");
  const [saved, setSaved] = useState(false);
  const [apiStatus, setApiStatus] = useState<"idle" | "checking" | "ok" | "error">("idle");

  useEffect(() => {
    const savedEndpoint = localStorage.getItem("api_endpoint");
    const savedApiKey = localStorage.getItem("api_key");
    if (savedEndpoint) setEndpoint(savedEndpoint);
    else if (process.env.NEXT_PUBLIC_API_BASE_URL) setEndpoint(process.env.NEXT_PUBLIC_API_BASE_URL);
    if (savedApiKey) setApiKey(savedApiKey);
  }, []);

  const handleSave = () => {
    localStorage.setItem("api_endpoint", endpoint);
    localStorage.setItem("api_key", apiKey);
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  const testConnection = async () => {
    setApiStatus("checking");
    try {
      const res = await fetch(`${endpoint}/health`, { signal: AbortSignal.timeout(5000) });
      setApiStatus(res.ok ? "ok" : "error");
    } catch {
      setApiStatus("error");
    }
    setTimeout(() => setApiStatus("idle"), 4000);
  };

  return (
    <MainLayout>
      <div className="max-w-3xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Settings</h1>
          <p className="text-slate-500 mt-1 text-sm">Configure your CodePilot AI connection and preferences.</p>
        </div>

        {/* API Connection */}
        <div className="panel rounded-2xl bg-white border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
            <Server size={18} className="text-indigo-600" />
            <h2 className="font-bold text-slate-800">Backend API Connection</h2>
          </div>
          <div className="px-6 py-5 space-y-4">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">API Endpoint</label>
              <p className="text-xs text-slate-500 mb-2">The base URL of your CodePilot AI backend instance.</p>
              <input
                type="text"
                value={endpoint}
                onChange={(e) => setEndpoint(e.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                placeholder="http://127.0.0.1:8000"
              />
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={testConnection}
                disabled={apiStatus === "checking"}
                className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 transition shadow-sm disabled:opacity-50"
              >
                <RefreshCw size={14} className={apiStatus === "checking" ? "animate-spin text-indigo-500" : ""} />
                {apiStatus === "checking" ? "Checking..." : "Test Connection"}
              </button>
              {apiStatus === "ok" && <span className="flex items-center gap-1.5 text-sm font-medium text-emerald-600"><CheckCircle size={15} /> Connected</span>}
              {apiStatus === "error" && <span className="text-sm font-medium text-rose-600">⚠ Connection failed — check URL and ensure backend is running.</span>}
            </div>
          </div>
        </div>

        {/* API Key */}
        <div className="panel rounded-2xl bg-white border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
            <Key size={18} className="text-indigo-600" />
            <h2 className="font-bold text-slate-800">API Key (Optional)</h2>
          </div>
          <div className="px-6 py-5 space-y-3">
            <p className="text-xs text-slate-500">
              Required only if the backend has <code className="bg-slate-100 px-1.5 py-0.5 rounded text-xs font-mono">API_KEY</code> set in its environment. Sent as <code className="bg-slate-100 px-1.5 py-0.5 rounded text-xs font-mono">X-Api-Key</code> header on all requests. Leave blank for local unrestricted access.
            </p>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
              placeholder="Enter API Key (leave blank if not set)"
            />
          </div>
        </div>

        {/* Save Button */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleSave}
            className="flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-2.5 text-sm font-bold text-white hover:bg-indigo-700 transition shadow-sm"
          >
            {saved ? <CheckCircle size={16} /> : <Save size={16} />}
            {saved ? "Saved!" : "Save Settings"}
          </button>
          {saved && <span className="text-sm text-emerald-600 font-medium">Settings saved to browser storage.</span>}
        </div>

        {/* About */}
        <div className="panel rounded-2xl bg-white border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
            <Info size={18} className="text-indigo-600" />
            <h2 className="font-bold text-slate-800">About CodePilot AI</h2>
          </div>
          <div className="px-6 py-5 space-y-3 text-sm text-slate-600">
            <p>
              <strong className="text-slate-800">CodePilot AI</strong> is an AI-powered GitHub repository analysis platform. Connect a repository, index it, and unlock 19 AI-driven workflows — from architecture diagrams to security analysis and test generation.
            </p>
            <div className="grid grid-cols-2 gap-3 pt-2">
              {[
                { label: "AI Engine", value: "Google Gemini" },
                { label: "Vector Search", value: "ChromaDB RAG" },
                { label: "Backend", value: "FastAPI + Python" },
                { label: "Frontend", value: "Next.js 16 + Tailwind v4" },
              ].map(({ label, value }) => (
                <div key={label} className="rounded-xl bg-slate-50 border border-slate-100 px-4 py-3">
                  <p className="text-xs text-slate-400 font-medium">{label}</p>
                  <p className="text-sm font-semibold text-slate-800 mt-0.5">{value}</p>
                </div>
              ))}
            </div>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs text-indigo-600 hover:text-indigo-700 font-medium pt-1"
            >
              View Source on GitHub <ExternalLink size={12} />
            </a>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
