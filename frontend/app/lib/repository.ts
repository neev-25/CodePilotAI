import api from "./api";

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

export interface IndexingJob {
  id: number;
  status: "QUEUED" | "RUNNING" | "RETRYING" | "PAUSED" | "COMPLETED" | "FAILED";
  message: string | null;
  result: Record<string, unknown> | null;
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

export interface Source {
  file: string;
  start_line: number;
  end_line: number;
  snippet: string;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
}

export interface ProjectAssessment {
  assessment: string;
  sources: Source[];
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

export interface OnboardingGuide {
  markdown: string;
}

export interface RepositoryDiagram {
  diagram_type: string;
  mermaid: string;
  sources: Source[];
}

export interface ReadinessEvidence {
  area: string;
  status: "present" | "missing" | "partial";
  detail: string;
  files: string[];
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
  evidence: ReadinessEvidence[];
  go_live: boolean;
}

export interface GeneratedTestCase {
  name: string;
  category: string;
  purpose: string;
  expected_result: string;
}

export interface TestGeneration {
  source_file: string;
  test_file_path: string;
  framework: string;
  summary: string;
  test_cases: GeneratedTestCase[];
  test_code: string;
}

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

export async function getLatestIndexJob(id: number): Promise<IndexingJob> {
  const res = await api.get<IndexingJob>(`/repositories/${id}/index-jobs/latest`);
  return res.data;
}

export async function getRepositoryStats(id: number): Promise<RepositoryStats> {
  const res = await api.get(`/repositories/${id}/stats`);
  return res.data;
}

export async function getProjectAssessment(
  id: number,
): Promise<ProjectAssessment> {
  const res = await api.post(`/repositories/${id}/assessment`);
  return res.data;
}

export async function getSequenceDiagram(id: number): Promise<RepositoryDiagram> {
  const res = await api.post(`/repositories/${id}/sequence-diagram`);
  return res.data;
}

export async function getClassDiagram(id: number): Promise<RepositoryDiagram> {
  const res = await api.post(`/repositories/${id}/class-diagram`);
  return res.data;
}

export async function getFlowchart(id: number): Promise<RepositoryDiagram> {
  const res = await api.post(`/repositories/${id}/flowchart`);
  return res.data;
}

export async function getProductionReadiness(
  id: number,
): Promise<ProductionReadiness> {
  const res = await api.post(`/repositories/${id}/production-readiness`);
  return res.data;
}

export async function generateTestCases(
  id: number,
  filePath: string,
): Promise<TestGeneration> {
  const res = await api.post(`/repositories/${id}/test-cases`, {
    file_path: filePath,
  });
  return res.data;
}

export async function getRepositoryTree(id: number): Promise<FileTreeResponse> {
  const res = await api.get(`/repositories/${id}/files`);
  return res.data;
}

export async function getFileContent(
  id: number,
  filePath: string,
): Promise<{ path: string; content: string }> {
  const res = await api.get(`/repositories/${id}/files/content`, {
    params: { file_path: filePath },
  });
  return res.data;
}

export async function getSecurityAnalysis(
  id: number,
): Promise<SecurityAnalysis> {
  const res = await api.post(`/repositories/${id}/security-analysis`);
  return res.data;
}

export async function getHealthScore(id: number): Promise<RepositoryHealth> {
  const res = await api.post(`/repositories/${id}/health-score`);
  return res.data;
}

export async function getDependencyGraph(
  id: number,
): Promise<DependencyGraph> {
  const res = await api.get(`/repositories/${id}/dependencies`);
  return res.data;
}

export async function askRepository(
  id: number,
  question: string,
): Promise<AskResponse> {
  const res = await api.post(`/repositories/${id}/ask`, { question });
  return res.data;
}

export async function getOnboarding(id: number): Promise<OnboardingGuide> {
  const res = await api.post(`/repositories/${id}/onboarding`);
  return res.data;
}
