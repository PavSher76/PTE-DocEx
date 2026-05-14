import { FormEvent, useState } from "react";

type Status = "OK" | "Требует проверки" | "Критично";

type LanguageIssue = {
  message: string;
  short_message?: string | null;
  context?: string | null;
  category?: string | null;
  replacements: string[];
  severity: "info" | "warning" | "critical";
  reason?: string | null;
};

type StyleAssessment = {
  status: Status;
  tone: string;
  ethics: string;
  terminology: string;
  recommendations: string[];
};

type CorrespondenceResult = {
  id: number;
  status: Status;
  source_text: string;
  languagetool_report: Record<string, unknown>;
  ollama_prompt: string;
  language_tool_matches: LanguageIssue[];
  filtered_matches: LanguageIssue[];
  style_assessment: StyleAssessment;
  created_at: string;
};

type PageComparison = {
  page: number;
  similarity: number;
  status: Status;
  pdf_text: string;
  editable_text: string;
  differences: string[];
};

type DocumentResult = {
  id: number;
  status: Status;
  similarity: number;
  conclusion: string;
  page_results: PageComparison[];
  created_at: string;
};

type Tab = "correspondence" | "documents";

const apiBase = import.meta.env.VITE_API_BASE_URL ?? "";
const defaultCorrespondencePrompt = `Проверь исходящее деловое письмо.
Оцени:
- ложные срабатывания LanguageTool;
- грамматику и синтаксис;
- деловой стиль и ясность;
- этичность формулировок;
- корректность примененных терминов;
- риски некорректной трактовки адресатом.
Верни только структурированный JSON по заданной схеме.`;

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>("correspondence");

  return (
    <main className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Локальный MVP</p>
          <h1>Контроль исходящей переписки и документации</h1>
          <p>
            Загружайте PDF исходящих писем для проверки через OCR, LanguageTool и Ollama,
            сравнивайте PDF с редактируемым оригиналом и получайте заключение о совпадении.
          </p>
        </div>
      </header>

      <nav className="tabs" aria-label="Сценарии проверки">
        <button className={activeTab === "correspondence" ? "active" : ""} onClick={() => setActiveTab("correspondence")}>
          Переписка
        </button>
        <button className={activeTab === "documents" ? "active" : ""} onClick={() => setActiveTab("documents")}>
          Документация
        </button>
      </nav>

      {activeTab === "correspondence" ? <CorrespondencePanel /> : <DocumentsPanel />}
    </main>
  );
}

function CorrespondencePanel() {
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [checkPrompt, setCheckPrompt] = useState(defaultCorrespondencePrompt);
  const [businessContext, setBusinessContext] = useState("Исходящая деловая корреспонденция.");
  const [strictness, setStrictness] = useState("standard");
  const [result, setResult] = useState<CorrespondenceResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!pdfFile) {
      return;
    }

    const formData = new FormData();
    formData.append("pdf_file", pdfFile);
    formData.append("check_prompt", checkPrompt);
    formData.append("business_context", businessContext);
    formData.append("strictness", strictness);
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${apiBase}/api/correspondence/check-pdf`, {
        method: "POST",
        body: formData
      });
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      setResult((await response.json()) as CorrespondenceResult);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Не удалось выполнить проверку.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="grid">
      <form className="card" onSubmit={submit}>
        <h2>Проверка переписки</h2>
        <label>
          PDF исходящего письма
          <input type="file" accept="application/pdf,.pdf" onChange={(event) => setPdfFile(event.target.files?.[0] ?? null)} required />
        </label>
        <details className="settings-panel">
          <summary>Настройки проверки</summary>
          <label>
            Промпт проверки письма и результата LanguageTool
            <textarea value={checkPrompt} onChange={(event) => setCheckPrompt(event.target.value)} rows={10} required />
          </label>
          <label>
            Контекст проверки
            <textarea value={businessContext} onChange={(event) => setBusinessContext(event.target.value)} rows={3} />
          </label>
          <label>
            Строгость
            <select value={strictness} onChange={(event) => setStrictness(event.target.value)}>
              <option value="standard">Обычная</option>
              <option value="strict">Строгая</option>
              <option value="critical">Критичная</option>
            </select>
          </label>
        </details>
        <button type="submit" disabled={loading || !pdfFile}>
          {loading ? "Распознаем и проверяем..." : "Проверить PDF"}
        </button>
        <p className="muted">PDF будет распознан через OCR, после чего текст пройдет LanguageTool и Ollama-фильтр.</p>
        {error && <p className="error">{error}</p>}
      </form>

      <div className="card">
        <h2>Результат</h2>
        {!result && <p className="muted">Здесь появятся замечания LanguageTool, фильтр Ollama и оценка стиля.</p>}
        {result && (
          <>
            <StatusBadge status={result.status} />
            <section className="result-block">
              <h3>Распознанный текст</h3>
              <pre className="text-preview">{result.source_text}</pre>
            </section>
            <section className="result-block">
              <h3>Стилистика и этика</h3>
              <p><strong>Тон:</strong> {result.style_assessment.tone}</p>
              <p><strong>Этика:</strong> {result.style_assessment.ethics}</p>
              <p><strong>Термины:</strong> {result.style_assessment.terminology}</p>
              <ul>
                {result.style_assessment.recommendations.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </section>
            <section className="result-block">
              <details>
                <summary>Замечания LanguageTool ({result.language_tool_matches.length})</summary>
                {result.language_tool_matches.length === 0 && <p className="muted">Замечаний нет.</p>}
                {result.language_tool_matches.map((issue, index) => (
                  <article className="issue" key={`${issue.message}-${index}`}>
                    <div className="issue-header">
                      <strong>{issue.short_message || issue.message}</strong>
                      <span>{issue.severity}</span>
                    </div>
                    {issue.context && <p className="context">{issue.context}</p>}
                    {issue.replacements.length > 0 && <p>Варианты: {issue.replacements.join(", ")}</p>}
                  </article>
                ))}
              </details>
              <details>
                <summary>Замечания после фильтра Ollama ({result.filtered_matches.length})</summary>
                {result.filtered_matches.length === 0 && <p className="muted">Замечаний нет.</p>}
                {result.filtered_matches.map((issue, index) => (
                  <article className="issue" key={`${issue.message}-${index}`}>
                    <div className="issue-header">
                      <strong>{issue.short_message || issue.message}</strong>
                      <span>{issue.severity}</span>
                    </div>
                    {issue.context && <p className="context">{issue.context}</p>}
                    {issue.reason && <p>{issue.reason}</p>}
                    {issue.replacements.length > 0 && <p>Варианты: {issue.replacements.join(", ")}</p>}
                  </article>
                ))}
              </details>
            </section>
            <section className="result-block">
              <h3>Данные для Ollama</h3>
              <details>
                <summary>Структурированный JSON LanguageTool</summary>
                <pre>{JSON.stringify(result.languagetool_report, null, 2)}</pre>
              </details>
              <details>
                <summary>Промпт, отправленный в Ollama</summary>
                <pre>{result.ollama_prompt}</pre>
              </details>
            </section>
          </>
        )}
      </div>
    </section>
  );
}

function DocumentsPanel() {
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [editableFile, setEditableFile] = useState<File | null>(null);
  const [result, setResult] = useState<DocumentResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!pdfFile || !editableFile) {
      return;
    }

    const formData = new FormData();
    formData.append("pdf_file", pdfFile);
    formData.append("editable_file", editableFile);
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${apiBase}/api/documents/compare`, {
        method: "POST",
        body: formData
      });
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      setResult((await response.json()) as DocumentResult);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Не удалось сравнить документы.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="grid">
      <form className="card" onSubmit={submit}>
        <h2>Сравнение комплекта</h2>
        <label>
          PDF-версия
          <input type="file" accept="application/pdf,.pdf" onChange={(event) => setPdfFile(event.target.files?.[0] ?? null)} required />
        </label>
        <label>
          Редактируемый файл
          <input type="file" accept=".docx,.odt,.rtf" onChange={(event) => setEditableFile(event.target.files?.[0] ?? null)} required />
        </label>
        <button type="submit" disabled={loading || !pdfFile || !editableFile}>
          {loading ? "Сравниваем..." : "Сравнить документы"}
        </button>
        <p className="muted">OCR может занимать несколько минут на больших файлах.</p>
        {error && <p className="error">{error}</p>}
      </form>

      <div className="card">
        <h2>Заключение</h2>
        {!result && <p className="muted">Здесь появится процент совпадения и список проблемных страниц.</p>}
        {result && (
          <>
            <StatusBadge status={result.status} />
            <p className="metric">{Math.round(result.similarity * 10000) / 100}% совпадения</p>
            <p>{result.conclusion}</p>
            <div className="pages">
              {result.page_results.map((page) => (
                <article className="page-card" key={page.page}>
                  <div className="issue-header">
                    <strong>Страница {page.page}</strong>
                    <span>{Math.round(page.similarity * 10000) / 100}%</span>
                  </div>
                  <StatusBadge status={page.status} compact />
                  {page.differences.length > 0 && (
                    <pre>{page.differences.join("\n")}</pre>
                  )}
                </article>
              ))}
            </div>
          </>
        )}
      </div>
    </section>
  );
}

function StatusBadge({ status, compact = false }: { status: Status; compact?: boolean }) {
  return <span className={`status status-${statusClass(status)} ${compact ? "compact" : ""}`}>{status}</span>;
}

function statusClass(status: Status) {
  if (status === "OK") {
    return "ok";
  }
  if (status === "Критично") {
    return "critical";
  }
  return "review";
}

async function extractError(response: Response) {
  try {
    const data = await response.json();
    return typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
  } catch {
    return `HTTP ${response.status}`;
  }
}
