import api from "./api";

// ── Types ──────────────────────────────────────────────────────────────────

export interface Repository {
  id: number;
  name: string;
  github_url: string;
  local_path: string;
  status: string;
  created_at: string;
}

export interface RepositoryStats {
  repository: string;
  status: string;
  files: number;
  documents: number;
  chunks: number;
  vectors: number;
  languages: Record<string, number>;
  loc?: number;
  commits?: number;
  branches?: number;
  contributors?: number;
  current_commit?: string | null;
}

export interface FileTreeNode {
  name: string;
  type: "file" | "directory";
  children?: FileTreeNode[];
}

export interface FileTreeResponse {
  repository: string;
  tree: FileTreeNode[];
}

export interface ReviewIssue {
  severity: string;
  category: string;
  file: string;
  message: string;
}

export interface RepositoryReview {
  overall_score: number;
  overall_review: string;
  strengths: string[];
  issues: ReviewIssue[];
  recommendations: string[];
}

export interface SecurityIssue {
  severity: string;
  file: string;
  line: number;
  issue: string;
  explanation?: string;
}

export interface SecurityAnalysis {
  risk_score: number;
  bugs: SecurityIssue[];
  security: SecurityIssue[];
  reliability: SecurityIssue[];
  recommendations: string[];
}

export interface DependencyNode {
  path: string;
}

export interface DependencyEdge {
  from_file: string;
  to_file: string;
}

export interface DependencyGraph {
  repository: string;
  nodes: DependencyNode[];
  edges: DependencyEdge[];
  external_dependencies: string[];
}

export interface DependencyAnalysis {
  overall_score: number;
  summary: string;
  internal_dependencies: { from: string; to: string }[];
  external_dependencies: string[];
  circular_dependencies: string[][];
  highly_coupled_modules: { module: string; reason: string }[];
  recommendations: string[];
}

export interface ComplexityAnalysis {
  overall_score: number;
  summary: string;
  maintainability: string;
  technical_debt: string;
  complex_files: { file: string; complexity: string; reason: string }[];
  code_smells: string[];
  recommendations: string[];
}

export interface RepositoryHealth {
  overall_score: number;
  grade: string;
  summary: string;
  maintainability_score: number;
  security_score: number;
  architecture_score: number;
  complexity_score: number;
  strengths: string[];
  weaknesses: string[];
  priority_actions: string[];
}

export interface ProductionReadiness {
  production_score: number;
  readiness: string;
  summary: string;
  scalability: string;
  maintainability: string;
  security: string;
  testing: string;
  observability: string;
  deployment: string;
  risks: string[];
  blockers: string[];
  recommendations: string[];
  go_live: boolean;
}

export interface RefactorSuggestion {
  priority: string;
  file: string;
  reason: string;
  recommendation: string;
}

export interface RefactorResponse {
  overall_score: number;
  summary: string;
  suggestions: RefactorSuggestion[];
}

export interface AskResponse {
  answer: string;
  sources: {
    file: string;
    start_line: number;
    end_line: number;
    snippet: string;
  }[];
}

// ── Repository Management ──────────────────────────────────────────────────

export async function getRepositories(): Promise<Repository[]> {
  const res = await api.get("/repositories");
  return res.data;
}

export async function cloneRepository(url: string): Promise<Repository> {
  const res = await api.post("/repositories", { github_url: url });
  return res.data;
}

export async function deleteRepository(id: number): Promise<void> {
  await api.delete(`/repositories/${id}`);
}

export async function getRepository(id: number): Promise<Repository> {
  const res = await api.get(`/repositories/${id}`);
  return res.data;
}

export async function indexRepository(id: number) {
  const res = await api.post(`/repositories/${id}/index`);
  return res.data;
}

// ── Stats & Summary ────────────────────────────────────────────────────────

export async function getRepositoryStats(id: number): Promise<RepositoryStats> {
  const res = await api.get(`/repositories/${id}/stats`);
  return res.data;
}

export async function getRepositorySummary(id: number) {
  const res = await api.post(`/repositories/${id}/summary`);
  return res.data;
}

// ── Files & Code ───────────────────────────────────────────────────────────

export async function getRepositoryTree(id: number): Promise<FileTreeResponse> {
  const res = await api.get(`/repositories/${id}/files`);
  return res.data;
}

export async function getFileContent(id: number, filePath: string) {
  const res = await api.get(`/repositories/${id}/files/content`, {
    params: { file_path: filePath }
  });
  return res.data;
}

export async function explainFile(id: number, filePath: string) {
  const res = await api.post(`/repositories/${id}/files/explain`, {
    path: filePath,
  });
  return res.data;
}

export async function explainFunction(
  id: number,
  filePath: string,
  functionName: string,
) {
  const res = await api.post(`/repositories/${id}/functions/explain`, {
    path: filePath,
    function: functionName,
  });
  return res.data;
}

export async function getDocumentation(id: number, filePath: string) {
  const res = await api.post(`/repositories/${id}/files/document`, {
    file_path: filePath,
  });
  return res.data;
}

export async function generateTests(id: number, filePath: string) {
  const res = await api.post(`/repositories/${id}/files/tests`, {
    file_path: filePath,
  });
  return res.data;
}

// ── Analysis ───────────────────────────────────────────────────────────────

export async function getSecurityAnalysis(
  id: number,
): Promise<SecurityAnalysis> {
  const res = await api.post(`/repositories/${id}/security-analysis`);
  return res.data;
}

export async function getRepositoryReview(
  id: number,
): Promise<RepositoryReview> {
  const res = await api.post(`/repositories/${id}/review`);
  return res.data;
}

export async function getComplexityAnalysis(
  id: number,
): Promise<ComplexityAnalysis> {
  const res = await api.post(`/repositories/${id}/complexity-analysis`);
  return res.data;
}

export async function getHealthScore(id: number): Promise<RepositoryHealth> {
  const res = await api.post(`/repositories/${id}/health-score`);
  return res.data;
}

export async function getProductionReadiness(
  id: number,
): Promise<ProductionReadiness> {
  const res = await api.post(`/repositories/${id}/production-readiness`);
  return res.data;
}

export async function getRefactorAdvice(
  id: number,
): Promise<RefactorResponse> {
  const res = await api.post(`/repositories/${id}/refactor`);
  return res.data;
}

// ── Dependencies ───────────────────────────────────────────────────────────

export async function getDependencyGraph(
  id: number,
): Promise<DependencyGraph> {
  const res = await api.get(`/repositories/${id}/dependencies`);
  return res.data;
}

export async function getDependencyAnalysis(
  id: number,
): Promise<DependencyAnalysis> {
  const res = await api.post(`/repositories/${id}/dependency-analysis`);
  return res.data;
}

// ── Documentation & README ─────────────────────────────────────────────────

export async function getReadme(id: number) {
  const res = await api.post(`/repositories/${id}/readme`);
  return res.data;
}

export async function getArchitecture(id: number) {
  const res = await api.post(`/repositories/${id}/architecture`);
  return res.data;
}

// ── Diagrams ───────────────────────────────────────────────────────────────

export async function getSequenceDiagram(id: number) {
  const res = await api.post(`/repositories/${id}/sequence-diagram`);
  return res.data;
}

export async function getClassDiagram(id: number) {
  const res = await api.post(`/repositories/${id}/class-diagram`);
  return res.data;
}

export async function getFlowchart(id: number) {
  const res = await api.post(`/repositories/${id}/flowchart`);
  return res.data;
}

// ── Dev Workflow ───────────────────────────────────────────────────────────

export async function generatePRDescription(
  id: number,
  title: string,
  summary = "",
) {
  const res = await api.post(`/repositories/${id}/pr-description`, {
    title,
    summary,
  });
  return res.data;
}

export async function generateCommitMessage(id: number, summary: string) {
  const res = await api.post(`/repositories/${id}/commit-message`, {
    summary,
  });
  return res.data;
}

export async function generateChangelog(
  id: number,
  version: string,
  summary: string,
) {
  const res = await api.post(`/repositories/${id}/changelog`, {
    version,
    summary,
  });
  return res.data;
}

// ── Q&A ────────────────────────────────────────────────────────────────────

export async function askRepository(
  id: number,
  question: string,
): Promise<AskResponse> {
  const res = await api.post(`/repositories/${id}/ask`, { question });
  return res.data;
}

export async function semanticSearch(id: number, query: string) {
  const res = await api.post(`/repositories/${id}/search`, { question: query });
  return res.data;
}

export async function generateDiffReview(id: number, diffText: string) {
  const res = await api.post(`/repositories/${id}/diff-review`, { diff_text: diffText });
  return res.data;
}

export async function generateChangeImpact(id: number, filePath: string, proposedChange: string) {
  const res = await api.post(`/repositories/${id}/change-impact`, { file_path: filePath, proposed_change: proposedChange });
  return res.data;
}
