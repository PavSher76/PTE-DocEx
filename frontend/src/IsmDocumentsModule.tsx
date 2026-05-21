import { type ChangeEvent, type DragEvent, FormEvent, useCallback, useEffect, useState } from "react";
import { IsmGraphCytoscape, type IsmGraphData } from "./IsmGraphCytoscape";

const apiBase = import.meta.env.VITE_API_BASE_URL ?? "";

export type IsmSubView = "registry" | "upload" | "queue" | "graph" | "review" | "errors";

type IsmProcess = {
  id: string;
  process_code: string;
  process_name: string;
  owner: string;
  description: string;
};

type IsmDocument = {
  document_id: string;
  title: string;
  code: string;
  document_type: string;
  revision: string;
  status: string;
  owner: string;
  discipline: string | null;
  filename: string | null;
  job_status: string | null;
  job_progress: number;
  tokens_count: number;
  interfaces_count: number;
  batch_id: string | null;
  review_status: string;
  created_at: string;
};

type IsmQueueItem = {
  job_id: string;
  document_id: string;
  filename: string;
  document_code: string;
  status: string;
  stage: string | null;
  progress: number;
  error_message: string | null;
};

type IsmGraph = {
  nodes: { id: string; node_type: string; label: string; meta: Record<string, unknown> }[];
  edges: {
    id: string;
    source: string;
    target: string;
    link_type: string;
    label: string;
    confidence: number;
  }[];
};

type IsmError = {
  id: string;
  filename: string;
  message: string;
  error_type: string;
  created_at: string;
};

const SUB_VIEWS: { id: IsmSubView; label: string; icon: string }[] = [
  { id: "registry", label: "Реестр документов", icon: "📋" },
  { id: "upload", label: "Пакетная загрузка", icon: "📤" },
  { id: "queue", label: "Очередь обработки", icon: "⏳" },
  { id: "graph", label: "Карта связей", icon: "🔗" },
  { id: "review", label: "Ревью", icon: "✓" },
  { id: "errors", label: "Ошибки разбора", icon: "⚠" }
];

function parseIsmHash(): IsmSubView {
  const hash = window.location.hash.replace(/^#\/?/, "");
  if (hash.startsWith("ism-documents/")) {
    const part = hash.split("/")[1] as IsmSubView;
    if (SUB_VIEWS.some((v) => v.id === part)) {
      return part;
    }
  }
  return "registry";
}

function setIsmHash(view: IsmSubView) {
  window.location.hash = `#/ism-documents/${view}`;
}

async function extractError(response: Response) {
  try {
    const data = await response.json();
    return typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
  } catch {
    return `HTTP ${response.status}`;
  }
}

export function IsmDocumentsModule() {
  const [subView, setSubView] = useState<IsmSubView>(parseIsmHash);
  const [processes, setProcesses] = useState<IsmProcess[]>([]);
  const [documents, setDocuments] = useState<IsmDocument[]>([]);
  const [queue, setQueue] = useState<IsmQueueItem[]>([]);
  const [graph, setGraph] = useState<IsmGraph | null>(null);
  const [errors, setErrors] = useState<IsmError[]>([]);
  const [reviewItems, setReviewItems] = useState<IsmDocument[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastBatchId, setLastBatchId] = useState<string | null>(null);

  const navigate = (view: IsmSubView) => {
    setSubView(view);
    setIsmHash(view);
  };

  useEffect(() => {
    const onHash = () => setSubView(parseIsmHash());
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  const loadProcesses = useCallback(async () => {
    const r = await fetch(`${apiBase}/api/ism/processes`);
    if (r.ok) {
      setProcesses((await r.json()) as IsmProcess[]);
    }
  }, []);

  const loadRegistry = useCallback(async () => {
    const r = await fetch(`${apiBase}/api/ism/documents`);
    if (r.ok) {
      setDocuments((await r.json()) as IsmDocument[]);
    }
  }, []);

  const loadQueue = useCallback(async () => {
    const q = lastBatchId ? `?batch_id=${lastBatchId}` : "";
    const r = await fetch(`${apiBase}/api/ism/documents/queue/dashboard${q}`);
    if (r.ok) {
      const data = (await r.json()) as { items: IsmQueueItem[] };
      setQueue(data.items);
    }
  }, [lastBatchId]);

  const loadGraph = useCallback(async () => {
    const q = lastBatchId ? `?batch_id=${lastBatchId}` : "";
    const r = await fetch(`${apiBase}/api/ism/documents/graph${q}`);
    if (r.ok) {
      setGraph((await r.json()) as IsmGraph);
    }
  }, [lastBatchId]);

  const loadReview = useCallback(async () => {
    if (!lastBatchId) {
      setReviewItems([]);
      return;
    }
    const r = await fetch(`${apiBase}/api/ism/batches/${lastBatchId}/review-queue`);
    if (r.ok) {
      const data = (await r.json()) as { items: IsmDocument[] };
      setReviewItems(data.items);
    }
  }, [lastBatchId]);

  const loadErrors = useCallback(async () => {
    const q = lastBatchId ? `?batch_id=${lastBatchId}` : "";
    const r = await fetch(`${apiBase}/api/ism/documents/errors/list${q}`);
    if (r.ok) {
      setErrors((await r.json()) as IsmError[]);
    }
  }, [lastBatchId]);

  useEffect(() => {
    void loadProcesses();
  }, [loadProcesses]);

  useEffect(() => {
    setError("");
    setLoading(true);
    const run = async () => {
      try {
        if (subView === "registry") {
          await loadRegistry();
        } else if (subView === "queue") {
          await loadQueue();
        } else if (subView === "graph") {
          await loadGraph();
        } else if (subView === "review") {
          await loadReview();
        } else if (subView === "errors") {
          await loadErrors();
        }
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Ошибка загрузки");
      } finally {
        setLoading(false);
      }
    };
    void run();
    const poll = subView === "queue" ? window.setInterval(() => void loadQueue(), 6000) : undefined;
    return () => {
      if (poll) {
        window.clearInterval(poll);
      }
    };
  }, [subView, loadRegistry, loadQueue, loadGraph, loadReview, loadErrors]);

  return (
    <div className="ism-module">
      <nav className="ism-subnav" aria-label="Разделы Документы ИСМ">
        {SUB_VIEWS.map((item) => (
          <button
            key={item.id}
            type="button"
            className={subView === item.id ? "active" : ""}
            onClick={() => navigate(item.id)}
          >
            <span className="ism-subnav-icon" aria-hidden>
              {item.icon}
            </span>
            {item.label}
          </button>
        ))}
      </nav>

      {error && <p className="error">{error}</p>}

      {lastBatchId && (
        <p className="muted ism-batch-hint">
          Текущий пакет: <code className="inline-code">{lastBatchId.slice(0, 8)}…</code>
          {" · "}
          <a href={`${apiBase}/api/ism/batches/${lastBatchId}/report.json`} target="_blank" rel="noreferrer">
            JSON отчёт
          </a>
          {" · "}
          <a href={`${apiBase}/api/ism/batches/${lastBatchId}/report.pdf`} target="_blank" rel="noreferrer">
            PDF отчёт
          </a>
        </p>
      )}

      {subView === "upload" && (
        <IsmUploadView
          processes={processes}
          loading={loading}
          onUploaded={(batchId) => {
            setLastBatchId(batchId);
            navigate("queue");
          }}
          setError={setError}
          setLoading={setLoading}
        />
      )}
      {subView === "registry" && (
        <IsmRegistryView documents={documents} loading={loading} onRefresh={() => void loadRegistry()} />
      )}
      {subView === "queue" && (
        <IsmQueueView
          items={queue}
          loading={loading}
          onRetry={async (jobId) => {
            await fetch(`${apiBase}/api/ism/jobs/${jobId}/retry`, { method: "POST" });
            await loadQueue();
          }}
          onCancel={async (jobId) => {
            await fetch(`${apiBase}/api/ism/jobs/${jobId}/cancel`, { method: "POST" });
            await loadQueue();
          }}
        />
      )}
      {subView === "graph" && <IsmGraphView graph={graph} loading={loading} />}
      {subView === "review" && (
        <IsmReviewView
          batchId={lastBatchId}
          items={reviewItems}
          loading={loading}
          onRefresh={() => void loadReview()}
          onReviewed={() => void loadReview()}
        />
      )}
      {subView === "errors" && <IsmErrorsView errors={errors} loading={loading} />}
    </div>
  );
}

function IsmUploadView({
  processes,
  loading,
  onUploaded,
  setError,
  setLoading
}: {
  processes: IsmProcess[];
  loading: boolean;
  onUploaded: (batchId: string) => void;
  setError: (s: string) => void;
  setLoading: (b: boolean) => void;
}) {
  const [files, setFiles] = useState<File[]>([]);
  const [ismProcessId, setIsmProcessId] = useState("");
  const [documentType, setDocumentType] = useState("SOP");
  const [owner, setOwner] = useState("ИСМ");
  const [status, setStatus] = useState("active");
  const [revision, setRevision] = useState("A");
  const [discipline, setDiscipline] = useState("");
  const [comment, setComment] = useState("");
  const [title, setTitle] = useState("");
  const [dragOver, setDragOver] = useState(false);

  const addFiles = (list: FileList | File[]) => {
    setFiles((prev) => [...prev, ...Array.from(list)]);
  };

  const onDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files.length) {
      addFiles(e.dataTransfer.files);
    }
  };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (files.length === 0) {
      setError("Добавьте файлы или ZIP.");
      return;
    }
    setLoading(true);
    setError("");
    const zipOnly = files.length === 1 && files[0].name.toLowerCase().endsWith(".zip");
    const form = new FormData();
    if (zipOnly) {
      form.append("archive", files[0]);
    } else {
      for (const f of files) {
        form.append("files", f);
      }
    }
    if (ismProcessId) {
      form.append("ism_process_id", ismProcessId);
    }
    form.append("document_type", documentType);
    form.append("owner", owner);
    form.append("status", status);
    form.append("revision", revision);
    if (discipline) {
      form.append("discipline", discipline);
    }
    if (comment) {
      form.append("comment", comment);
    }
    if (title) {
      form.append("title", title);
    }
    try {
      const url = zipOnly
        ? `${apiBase}/api/ism/documents/upload-zip`
        : `${apiBase}/api/ism/documents/batch-upload`;
      const response = await fetch(url, { method: "POST", body: form });
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      const data = (await response.json()) as { batch_id: string };
      setFiles([]);
      onUploaded(data.batch_id);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Ошибка загрузки");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card span-wide">
      <h2>Пакетная загрузка</h2>
      <p className="muted doc-lede">DOC, DOCX, XLS, XLSX, PDF — перетащите файлы, папку или ZIP.</p>
      <div
        className={`ism-dropzone ${dragOver ? "drag-over" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
      >
        <p>Перетащите файлы сюда</p>
        <label className="ism-file-label">
          Выбрать файлы
          <input
            type="file"
            multiple
            accept=".pdf,.doc,.docx,.xls,.xlsx"
            onChange={(e: ChangeEvent<HTMLInputElement>) => e.target.files && addFiles(e.target.files)}
          />
        </label>
        <label className="ism-file-label">
          Выбрать папку
          <input
            type="file"
            multiple
            // @ts-expect-error webkitdirectory
            webkitdirectory=""
            onChange={(e: ChangeEvent<HTMLInputElement>) => e.target.files && addFiles(e.target.files)}
          />
        </label>
      </div>
      {files.length > 0 && (
        <ul className="ism-file-list">
          {files.map((f) => (
            <li key={`${f.name}-${f.size}`}>
              {f.name} · {(f.size / 1024).toFixed(1)} КБ
            </li>
          ))}
        </ul>
      )}
      <form className="stack-form" onSubmit={(e) => void submit(e)}>
        <label>
          Процесс ИСМ
          <select value={ismProcessId} onChange={(e) => setIsmProcessId(e.target.value)}>
            <option value="">— не выбран —</option>
            {processes.map((p) => (
              <option key={p.id} value={p.id}>
                {p.process_name} ({p.process_code})
              </option>
            ))}
          </select>
        </label>
        <label>
          Тип документа
          <select value={documentType} onChange={(e) => setDocumentType(e.target.value)}>
            {["SOP", "FORM", "CHECKLIST", "REGISTER", "INSTRUCTION", "REQUIREMENT", "OTHER"].map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>
        <div className="ism-form-row">
          <label>
            Владелец
            <input value={owner} onChange={(e) => setOwner(e.target.value)} />
          </label>
          <label>
            Статус
            <input value={status} onChange={(e) => setStatus(e.target.value)} />
          </label>
          <label>
            Ревизия
            <input value={revision} onChange={(e) => setRevision(e.target.value)} />
          </label>
          <label>
            Дисциплина
            <input value={discipline} onChange={(e) => setDiscipline(e.target.value)} />
          </label>
        </div>
        <label>
          Наименование пакета
          <input value={title} onChange={(e) => setTitle(e.target.value)} />
        </label>
        <label>
          Комментарий
          <textarea value={comment} onChange={(e) => setComment(e.target.value)} rows={2} />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "Загрузка…" : "Загрузить пакет"}
        </button>
      </form>
    </section>
  );
}

function IsmRegistryView({
  documents,
  loading,
  onRefresh
}: {
  documents: IsmDocument[];
  loading: boolean;
  onRefresh: () => void;
}) {
  return (
    <section className="card span-wide">
      <div className="bundle-dashboard-header">
        <h2>Реестр документов</h2>
        <button type="button" className="text-button" onClick={onRefresh} disabled={loading}>
          Обновить
        </button>
      </div>
      {loading && documents.length === 0 && <p className="muted">Загрузка…</p>}
      {documents.length === 0 && !loading && <p className="muted">Документов пока нет.</p>}
      {documents.length > 0 && (
        <div className="bundle-dashboard-table-wrap">
          <table className="bundle-dashboard-table">
            <thead>
              <tr>
                <th>Код</th>
                <th>Название</th>
                <th>Тип</th>
                <th>Рев.</th>
                <th>RAG</th>
                <th>Ревью</th>
                <th>Связи</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((d) => (
                <tr key={d.document_id}>
                  <td>
                    <code className="inline-code">{d.code || "—"}</code>
                  </td>
                  <td>{d.title || d.filename}</td>
                  <td className="muted">{d.document_type}</td>
                  <td>{d.revision}</td>
                  <td>
                    {d.job_status ?? "—"}
                    {d.tokens_count > 0 ? ` · ${d.tokens_count}` : ""}
                  </td>
                  <td>
                    <span className={`status-review status-${d.review_status}`}>{d.review_status}</span>
                  </td>
                  <td>{d.interfaces_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function IsmQueueView({
  items,
  loading,
  onRetry,
  onCancel
}: {
  items: IsmQueueItem[];
  loading: boolean;
  onRetry: (jobId: string) => Promise<void>;
  onCancel: (jobId: string) => Promise<void>;
}) {
  return (
    <section className="card span-wide">
      <h2>Очередь обработки</h2>
      {loading && items.length === 0 && <p className="muted">Загрузка…</p>}
      {items.length === 0 && !loading && <p className="muted">Очередь пуста.</p>}
      {items.map((item) => (
        <div key={item.job_id} className="ism-queue-item">
          <div className="ism-queue-head">
            <strong>{item.filename}</strong>
            <span className="muted">{item.status}</span>
          </div>
          <div className="ism-progress">
            <div className="ism-progress-bar" style={{ width: `${item.progress}%` }} />
          </div>
          {item.error_message && <p className="error">{item.error_message}</p>}
          <div className="button-row">
            {item.status === "failed" && (
              <button type="button" className="text-button" onClick={() => void onRetry(item.job_id)}>
                Повторить
              </button>
            )}
            {!["indexed", "cancelled"].includes(item.status) && (
              <button type="button" className="text-button" onClick={() => void onCancel(item.job_id)}>
                Отменить
              </button>
            )}
          </div>
        </div>
      ))}
    </section>
  );
}

function IsmGraphView({ graph, loading }: { graph: IsmGraph | null; loading: boolean }) {
  if (loading && !graph) {
    return <p className="muted">Построение карты…</p>;
  }
  if (!graph || graph.nodes.length === 0) {
    return <p className="muted">Нет данных для графа. Загрузите пакет документов.</p>;
  }
  const docs = graph.nodes.filter((n) => n.node_type === "document");
  const processes = graph.nodes.filter((n) => n.node_type === "process");
  return (
    <section className="card span-wide">
      <h2>Карта связей</h2>
      <p className="muted">
        Процессы: {processes.length} · Документы: {docs.length} · Связи: {graph.edges.length}
      </p>
      <IsmGraphCytoscape graph={graph as IsmGraphData} />
      <details className="ism-graph-details">
        <summary>Таблица связей</summary>
        <table className="bundle-dashboard-table">
          <thead>
            <tr>
              <th>Из</th>
              <th>Тип</th>
              <th>В</th>
              <th>%</th>
            </tr>
          </thead>
          <tbody>
            {graph.edges
              .filter((e) => e.link_type !== "controls")
              .map((e) => (
                <tr key={e.id}>
                  <td>{graph.nodes.find((n) => n.id === e.source)?.label ?? e.source}</td>
                  <td className="muted">{e.link_type}</td>
                  <td>{graph.nodes.find((n) => n.id === e.target)?.label ?? e.target}</td>
                  <td>{Math.round(e.confidence * 100)}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </details>
    </section>
  );
}

function IsmReviewView({
  batchId,
  items,
  loading,
  onRefresh,
  onReviewed
}: {
  batchId: string | null;
  items: IsmDocument[];
  loading: boolean;
  onRefresh: () => void;
  onReviewed: () => void;
}) {
  const [notes, setNotes] = useState<Record<string, string>>({});

  const submitReview = async (documentId: string, reviewStatus: string) => {
    const response = await fetch(`${apiBase}/api/ism/documents/${documentId}/review`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ review_status: reviewStatus, review_notes: notes[documentId] ?? "" })
    });
    if (!response.ok) {
      return;
    }
    onReviewed();
  };

  if (!batchId) {
    return (
      <section className="card span-wide">
        <h2>Ревью пакета</h2>
        <p className="muted">Сначала загрузите пакет документов.</p>
      </section>
    );
  }

  return (
    <section className="card span-wide">
      <div className="bundle-dashboard-header">
        <h2>Ревью документов</h2>
        <button type="button" className="text-button" onClick={onRefresh} disabled={loading}>
          Обновить
        </button>
      </div>
      {loading && items.length === 0 && <p className="muted">Загрузка…</p>}
      {items.length === 0 && !loading && <p className="muted">Нет документов для ревью.</p>}
      <ul className="ism-review-list">
        {items.map((doc) => (
          <li key={doc.document_id} className="ism-review-item">
            <div className="ism-review-head">
              <strong>{doc.code || doc.title || doc.filename}</strong>
              <span className={`status-review status-${doc.review_status}`}>{doc.review_status}</span>
            </div>
            <p className="muted">
              {doc.document_type} · RAG: {doc.job_status ?? "—"} · токенов: {doc.tokens_count}
            </p>
            <label>
              Комментарий ревьюера
              <textarea
                rows={2}
                value={notes[doc.document_id] ?? ""}
                onChange={(e) =>
                  setNotes((prev) => ({ ...prev, [doc.document_id]: e.target.value }))
                }
              />
            </label>
            <div className="button-row">
              <button type="button" onClick={() => void submitReview(doc.document_id, "approved")}>
                Одобрить
              </button>
              <button
                type="button"
                className="text-button"
                onClick={() => void submitReview(doc.document_id, "rejected")}
              >
                Отклонить
              </button>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}

function IsmErrorsView({ errors, loading }: { errors: IsmError[]; loading: boolean }) {
  return (
    <section className="card span-wide">
      <h2>Ошибки разбора</h2>
      {loading && errors.length === 0 && <p className="muted">Загрузка…</p>}
      {errors.length === 0 && !loading && <p className="muted">Ошибок нет.</p>}
      <ul className="ism-error-list">
        {errors.map((err) => (
          <li key={err.id}>
            <strong>{err.filename}</strong>
            <span className="muted"> · {err.error_type}</span>
            <p>{err.message}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
