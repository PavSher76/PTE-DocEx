const API = import.meta.env.VITE_API_URL || "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, init);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  if (res.headers.get("content-type")?.includes("text/markdown")) {
    return (await res.text()) as T;
  }
  return res.json() as Promise<T>;
}

export type Project = {
  id: string;
  project_id: string;
  name: string;
  description: string;
};

export type SearchHit = {
  token_id: string;
  score: number;
  text: string;
  document_id: string;
  document_code?: string;
  page_number?: number;
  element_type: string;
};

export type QueryResponse = {
  answer: string;
  hits: SearchHit[];
  llm_used: boolean;
  warnings: string[];
};

export const api = {
  listProjects: () => request<Project[]>("/projects"),
  bootstrapPilot: (projectId?: string) =>
    request<{ project_id: string; created: boolean; message: string }>(
      `/pilot/bootstrap${projectId ? `?project_id=${encodeURIComponent(projectId)}` : ""}`,
      { method: "POST" }
    ),
  upload: async (projectId: string, file: File) => {
    const fd = new FormData();
    fd.append("project_id", projectId);
    fd.append("file", file);
    return request<{ document_id: string; job_id: string }>("/documents/upload", {
      method: "POST",
      body: fd,
    });
  },
  docStatus: (docId: string) =>
    request<{ job: { status: string }; tokens_count: number }>(`/documents/${docId}/status`),
  query: (projectId: string, query: string, useLlm: boolean) =>
    request<QueryResponse>("/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        project_id: projectId,
        query,
        use_llm: useLlm,
        top_k: 8,
      }),
    }),
  runChecks: (projectId: string) =>
    request<{ run_id: string; report: { overall_status: string; checks: unknown[] } }>(
      `/projects/${projectId}/checks/run`,
      { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" }
    ),
  runPilot: (projectId: string) =>
    request<{
      documents_count: number;
      requirements_count: number;
      source_data_issues: { check_id: string; summary: string }[];
      query_answer?: string;
    }>(`/pilot/${projectId}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    }),
  feedback: (body: {
    project_id: string;
    source_type: string;
    rating: number;
    comment: string;
    lesson_tags: string[];
  }) =>
    request("/pilot/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  pagePreviewUrl: (documentId: string, page: number, tokenId?: string) => {
    const q = tokenId ? `?highlight=true&token_id=${tokenId}` : "";
    return `${API}/documents/${documentId}/pages/${page}/preview/image${q}`;
  },
};
