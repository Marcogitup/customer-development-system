import type { Company, Project, ProjectDetail, ResearchTask } from "./types";

const rawApiBase = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
export const API_BASE = rawApiBase.startsWith("http") ? rawApiBase : `https://${rawApiBase}`;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {})
    },
    cache: "no-store"
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function listProjects() {
  return request<Project[]>("/api/projects");
}

export function createProject(payload: { name: string; description?: string; seed_keywords: string[] }) {
  return request<Project>("/api/projects", { method: "POST", body: JSON.stringify(payload) });
}

export function getProject(id: number) {
  return request<ProjectDetail>(`/api/projects/${id}`);
}

export function runResearchNow(id: number) {
  return request<ResearchTask>(`/api/projects/${id}/research-tasks/run-now`, { method: "POST" });
}

export function queueResearch(id: number) {
  return request<ResearchTask>(`/api/projects/${id}/research-tasks`, { method: "POST" });
}

export function updateCompany(id: number, payload: Partial<Company>) {
  return request<Company>(`/api/companies/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
}

export function exportUrl(projectId: number, format: "csv" | "xlsx") {
  return `${API_BASE}/api/projects/${projectId}/exports/companies.${format}`;
}
