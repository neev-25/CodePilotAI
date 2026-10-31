"use client";

import { useMemo, useState } from "react";
import { Download, LoaderCircle, Sparkles } from "lucide-react";
import axios from "axios";

import CodeViewer from "@/app/components/repository/CodeViewer";
import ErrorCard from "@/app/components/repository/ErrorCard";
import PdfExportButton from "@/app/components/PdfExportButton";
import { generateTestCases, type TestGeneration } from "@/app/lib/repository";

interface Props {
  repoId: number;
  repoName: string;
  sourceFiles: string[];
}

function languageForPath(path: string) {
  const extension = path.split(".").pop()?.toLowerCase();
  if (extension === "py") return "python";
  if (extension === "ts" || extension === "tsx") return "typescript";
  if (extension === "jsx") return "jsx";
  if (extension === "go") return "go";
  if (extension === "rs") return "rust";
  if (extension === "java") return "java";
  return "javascript";
}

export default function TestGeneratorPanel({
  repoId,
  repoName,
  sourceFiles,
}: Props) {
  const [filePath, setFilePath] = useState(sourceFiles[0] ?? "");
  const [result, setResult] = useState<TestGeneration | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const language = useMemo(
    () => languageForPath(result?.test_file_path ?? filePath),
    [filePath, result?.test_file_path],
  );

  async function generate() {
    if (!filePath || loading) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await generateTestCases(repoId, filePath));
    } catch (requestError) {
      setError(
        axios.isAxiosError<{ detail?: string }>(requestError)
          ? requestError.response?.data?.detail ??
              "Test cases could not be generated. Please try again."
          : requestError instanceof Error
            ? requestError.message
            : "Test cases could not be generated. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  }

  function downloadTestFile() {
    if (!result) return;
    const url = URL.createObjectURL(
      new Blob([result.test_code], { type: "text/plain;charset=utf-8" }),
    );
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = result.test_file_path.split("/").pop() ?? "generated-test";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  if (sourceFiles.length === 0) {
    return (
      <ErrorCard
        title="No supported source files were found. Index a repository containing Python, JavaScript, TypeScript, Go, Rust, or Java source files."
        backHref={`/repositories/${repoId}`}
      />
    );
  }

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <label
          htmlFor="test-source-file"
          className="text-sm font-semibold text-slate-800"
        >
          Choose a source file
        </label>
        <div className="mt-3 flex flex-col gap-3 sm:flex-row">
          <select
            id="test-source-file"
            value={filePath}
            onChange={(event) => setFilePath(event.target.value)}
            className="min-w-0 flex-1 rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-800"
          >
            {sourceFiles.map((path) => (
              <option key={path} value={path}>
                {path}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={generate}
            disabled={loading || !filePath}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? (
              <LoaderCircle size={16} className="animate-spin" />
            ) : (
              <Sparkles size={16} />
            )}
            {loading ? "Analyzing source…" : "Generate test cases"}
          </button>
        </div>
        <p className="mt-3 text-xs leading-5 text-slate-500">
          Tests are generated against the selected file and detected test
          framework. They are not executed or saved to your repository.
        </p>
      </section>

      {error && (
        <div
          role="alert"
          className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800"
        >
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-slate-900">
                Tests for {result.source_file}
              </p>
              <p className="mt-1 text-xs text-slate-500">
                {result.framework} · proposed file: {result.test_file_path}
              </p>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={downloadTestFile}
                className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                <Download size={15} />
                Download tests
              </button>
              <PdfExportButton
                targetId="generated-tests-report"
                filename={`${repoName}-generated-tests.pdf`}
              />
            </div>
          </div>

          <div id="generated-tests-report" className="space-y-5">
            <section className="rounded-xl border border-indigo-100 bg-indigo-50 p-5">
              <p className="text-xs font-semibold uppercase tracking-wider text-indigo-700">
                Test plan
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-700">
                {result.summary}
              </p>
            </section>

            <section className="rounded-xl border border-slate-200 bg-white p-5">
              <h2 className="text-sm font-semibold text-slate-900">
                Generated test cases
              </h2>
              <div className="mt-3 grid gap-3 md:grid-cols-2">
                {result.test_cases.map((testCase, index) => (
                  <article
                    key={`${testCase.name}-${index}`}
                    className="rounded-lg border border-slate-200 p-4"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <h3 className="text-sm font-semibold text-slate-900">
                        {testCase.name}
                      </h3>
                      <span className="shrink-0 rounded-full bg-slate-100 px-2 py-1 text-[11px] font-medium capitalize text-slate-600">
                        {testCase.category}
                      </span>
                    </div>
                    <p className="mt-2 text-sm leading-5 text-slate-600">
                      {testCase.purpose}
                    </p>
                    <p className="mt-2 text-xs leading-5 text-slate-500">
                      Expected: {testCase.expected_result}
                    </p>
                  </article>
                ))}
              </div>
            </section>

            <section className="space-y-3">
              <div>
                <h2 className="text-sm font-semibold text-slate-900">
                  Generated test file
                </h2>
                <p className="mt-1 text-xs text-slate-500">
                  Review the imports and run it using your project&apos;s test
                  command.
                </p>
              </div>
              <CodeViewer code={result.test_code} language={language} />
            </section>
          </div>
        </div>
      )}
    </div>
  );
}
