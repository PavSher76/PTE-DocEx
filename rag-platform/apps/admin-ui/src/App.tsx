import { FormEvent, useCallback, useEffect, useState } from "react";
import { api, Project, QueryResponse, SearchHit } from "./api";

type Tab = "upload" | "query" | "checks" | "pilot" | "feedback";

export default function App() {
  const [tab, setTab] = useState<Tab>("upload");
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectId, setProjectId] = useState("PTE-ITC-450");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [uploadStatus, setUploadStatus] = useState("");
  const [queryText, setQueryText] = useState("Какие исходные данные требуются для раздела ТХ?");
  const [useLlm, setUseLlm] = useState(true);
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null);
  const [checkStatus, setCheckStatus] = useState("");
  const [pilotResult, setPilotResult] = useState<string>("");
  const [feedbackRating, setFeedbackRating] = useState(4);
  const [feedbackComment, setFeedbackComment] = useState("");
  const [feedbackTags, setFeedbackTags] = useState("retrieval,source_data");

  const loadProjects = useCallback(async () => {
    try {
      const list = await api.listProjects();
      setProjects(list);
      if (list.length && !list.find((p) => p.project_id === projectId)) {
        setProjectId(list[0].project_id);
      }
    } catch (e) {
      setError(String(e));
    }
  }, [projectId]);

  useEffect(() => {
    void loadProjects();
  }, [loadProjects]);

  async function handleBootstrap() {
    setLoading(true);
    setError("");
    try {
      const r = await api.bootstrapPilot(projectId);
      setUploadStatus(r.message);
      await loadProjects();
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload(file: File) {
    setLoading(true);
    setError("");
    setUploadStatus("Загрузка…");
    try {
      const r = await api.upload(projectId, file);
      setUploadStatus(`Документ ${r.document_id}, job ${r.job_id}`);
      for (let i = 0; i < 30; i++) {
        await new Promise((res) => setTimeout(res, 2000));
        const st = await api.docStatus(r.document_id);
        setUploadStatus(`Статус: ${st.job.status}, токенов: ${st.tokens_count}`);
        if (st.job.status === "indexed" || st.job.status === "failed") break;
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  async function handleQuery(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setQueryResult(null);
    try {
      const r = await api.query(projectId, queryText, useLlm);
      setQueryResult(r);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  async function handleChecks() {
    setLoading(true);
    setError("");
    try {
      const r = await api.runChecks(projectId);
      setCheckStatus(`Прогон ${r.run_id}: ${r.report.overall_status}, проверок: ${r.report.checks.length}`);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  async function handlePilot() {
    setLoading(true);
    setError("");
    setPilotResult("");
    try {
      const r = await api.runPilot(projectId);
      const issues = r.source_data_issues.map((i) => `• ${i.check_id}: ${i.summary}`).join("\n");
      setPilotResult(
        `Документов: ${r.documents_count}, требований: ${r.requirements_count}\n` +
          `Проблемы исходных данных:\n${issues || "—"}\n\n` +
          (r.query_answer ? `RAG-ответ:\n${r.query_answer}` : "")
      );
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  async function handleFeedback(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await api.feedback({
        project_id: projectId,
        source_type: "pilot_run",
        rating: feedbackRating,
        comment: feedbackComment,
        lesson_tags: feedbackTags.split(",").map((t) => t.trim()).filter(Boolean),
      });
      setFeedbackComment("");
      setUploadStatus("Обратная связь сохранена (Lessons Learned).");
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header>
        <h1>RAG Platform — Admin UI</h1>
        <p className="muted">Пилот ИТЦ: загрузка комплекта, RAG-запросы, AI-NK, обратная связь</p>
      </header>

      <div className="card">
        <label>
          Проект
          <select value={projectId} onChange={(e) => setProjectId(e.target.value)}>
            {projects.length === 0 && <option value={projectId}>{projectId}</option>}
            {projects.map((p) => (
              <option key={p.id} value={p.project_id}>
                {p.project_id} — {p.name}
              </option>
            ))}
          </select>
        </label>
        <button type="button" className="primary" onClick={() => void handleBootstrap()} disabled={loading}>
          Bootstrap пилота ИТЦ
        </button>
      </div>

      <nav className="tabs">
        {(
          [
            ["upload", "Загрузка"],
            ["query", "Запрос"],
            ["checks", "AI-NK"],
            ["pilot", "Пилот"],
            ["feedback", "Lessons Learned"],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            className={tab === id ? "active" : ""}
            onClick={() => setTab(id)}
          >
            {label}
          </button>
        ))}
      </nav>

      {error && <p className="error">{error}</p>}
      {uploadStatus && tab !== "feedback" && <p className="muted">{uploadStatus}</p>}

      {tab === "upload" && (
        <div className="card">
          <h2>Загрузка документа</h2>
          <label>
            PDF / DOCX / XLSX
            <input
              type="file"
              accept=".pdf,.docx,.xlsx,.txt"
              disabled={loading}
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) void handleUpload(f);
              }}
            />
          </label>
        </div>
      )}

      {tab === "query" && (
        <div className="card">
          <h2>RAG-запрос</h2>
          <form onSubmit={(e) => void handleQuery(e)}>
            <label>
              Вопрос
              <textarea value={queryText} onChange={(e) => setQueryText(e.target.value)} rows={3} />
            </label>
            <label>
              <input type="checkbox" checked={useLlm} onChange={(e) => setUseLlm(e.target.checked)} />{" "}
              Генерация через LLM (Ollama)
            </label>
            <button type="submit" className="primary" disabled={loading}>
              Спросить
            </button>
          </form>
          {queryResult && (
            <>
              <p className="muted">
                LLM: {queryResult.llm_used ? "да" : "extractive"}
                {queryResult.warnings?.length ? ` · ${queryResult.warnings.join("; ")}` : ""}
              </p>
              <div className="answer">{queryResult.answer}</div>
              {queryResult.hits.map((h) => (
                <HitCard key={h.token_id} hit={h} />
              ))}
            </>
          )}
        </div>
      )}

      {tab === "checks" && (
        <div className="card">
          <h2>AI-NK проверки</h2>
          <button type="button" className="primary" disabled={loading} onClick={() => void handleChecks()}>
            Запустить все проверки
          </button>
          {checkStatus && <p className="muted">{checkStatus}</p>}
        </div>
      )}

      {tab === "pilot" && (
        <div className="card">
          <h2>Пилот ИТЦ</h2>
          <p className="muted">Состав комплекта, исходные данные, реестр требований, демо-запрос</p>
          <button type="button" className="primary" disabled={loading} onClick={() => void handlePilot()}>
            Запустить пилотный прогон
          </button>
          {pilotResult && <pre className="answer">{pilotResult}</pre>}
        </div>
      )}

      {tab === "feedback" && (
        <div className="card">
          <h2>Lessons Learned</h2>
          <form onSubmit={(e) => void handleFeedback(e)}>
            <label>
              Оценка (1–5)
              <input
                type="number"
                min={1}
                max={5}
                value={feedbackRating}
                onChange={(e) => setFeedbackRating(Number(e.target.value))}
              />
            </label>
            <label>
              Теги (через запятую)
              <input value={feedbackTags} onChange={(e) => setFeedbackTags(e.target.value)} />
            </label>
            <label>
              Комментарий
              <textarea
                value={feedbackComment}
                onChange={(e) => setFeedbackComment(e.target.value)}
                rows={4}
              />
            </label>
            <button type="submit" className="primary" disabled={loading}>
              Отправить
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

function HitCard({ hit }: { hit: SearchHit }) {
  const preview =
    hit.page_number != null
      ? api.pagePreviewUrl(hit.document_id, hit.page_number, hit.token_id)
      : null;
  return (
    <div className="hit">
      <div className="hit-meta">
        {hit.document_code || "—"} · стр. {hit.page_number ?? "—"} · {hit.element_type} · score{" "}
        {hit.score.toFixed(3)}
      </div>
      <p>{hit.text.slice(0, 400)}</p>
      {preview && (
        <img className="preview-img" src={preview} alt="preview" loading="lazy" />
      )}
    </div>
  );
}
