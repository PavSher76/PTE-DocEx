import { type ChangeEvent, FormEvent, useState } from "react";

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

type Fz63CheckItem = {
  id: string;
  title: string;
  passed: boolean | null;
  detail: string;
};

type BundlePdfUkepValidation = {
  sig_flags: number | null;
  signature_widget_count: number;
  has_signed_embedded_signature: boolean;
  signer_full_name: string | null;
  certificate_valid: boolean | null;
  certificate_validity_label: string;
  signed_at: string | null;
  is_qualified_certificate: boolean | null;
  fz63_compliant: boolean | null;
  fz63_summary: string;
  fz63_checks: Fz63CheckItem[];
  status: Status;
  message: string;
  structural_validation_only: boolean;
  note: string;
};

type BundlePdfUploadItem = {
  original_filename: string;
  size_bytes: number;
  relative_path: string;
  crc32_hex: string;
  ukep: BundlePdfUkepValidation;
};

type DocumentBundleUploadResponse = {
  batch_id: string;
  total_files: number;
  files: BundlePdfUploadItem[];
  bundle_manifest_crc32_hex: string;
  overall_ukep_status: Status;
  ukep_disclaimer: string;
};

type Tab = "correspondence" | "documents";
type DocumentsSubTab = "compare" | "bundleUpload";

const apiBase = import.meta.env.VITE_API_BASE_URL ?? "";
const defaultCorrespondencePrompt = `Проверь исходящее деловое письмо.
Оцени:
- ложные срабатывания LanguageTool;
- грамматику и синтаксис;
- деловой стиль и ясность;
- этичность формулировок;
- корректность примененных терминов;
- риски некорректной трактовки адресатом.
- не считай двойные и тройные пробелы ошибками; замечания LanguageTool только про лишние интервалы, повторные пробелы или пробелы после OCR помечай accepted=false.
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
  const [documentsSubTab, setDocumentsSubTab] = useState<DocumentsSubTab>("compare");

  return (
    <>
      <nav className="tabs subtabs" aria-label="Разделы документации">
        <button
          type="button"
          className={documentsSubTab === "compare" ? "active" : ""}
          onClick={() => setDocumentsSubTab("compare")}
        >
          Сравнение комплекта
        </button>
        <button
          type="button"
          className={documentsSubTab === "bundleUpload" ? "active" : ""}
          onClick={() => setDocumentsSubTab("bundleUpload")}
        >
          Загрузка комплекта документации
        </button>
      </nav>
      {documentsSubTab === "compare" ? <DocumentsCompareSection /> : <DocumentBundleUploadSection />}
    </>
  );
}

function DocumentsCompareSection() {
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

function DocumentBundleUploadSection() {
  const [pdfFiles, setPdfFiles] = useState<File[]>([]);
  const [bundleResult, setBundleResult] = useState<DocumentBundleUploadResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function onFilesChange(event: ChangeEvent<HTMLInputElement>) {
    const list = event.target.files;
    setPdfFiles(list ? Array.from(list).filter((f) => f.type === "application/pdf" || f.name.toLowerCase().endsWith(".pdf")) : []);
    setBundleResult(null);
    setError("");
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (pdfFiles.length === 0) {
      return;
    }

    const formData = new FormData();
    for (const file of pdfFiles) {
      formData.append("pdf_files", file);
    }
    setLoading(true);
    setError("");
    setBundleResult(null);

    try {
      const response = await fetch(`${apiBase}/api/documents/bundles/upload`, {
        method: "POST",
        body: formData
      });
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      setBundleResult((await response.json()) as DocumentBundleUploadResponse);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Не удалось загрузить комплект.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="grid">
      <form className="card" onSubmit={submit}>
        <h2>Загрузка комплекта документации</h2>
        <p className="muted doc-lede">
          Пакетная загрузка PDF томов и листов исходящего комплекта (проектная или рабочая документация). Файлы сохраняются в одной папке на сервере для дальнейшего контроля.
        </p>
        <label>
          PDF-файлы комплекта (несколько штук)
          <input type="file" accept="application/pdf,.pdf" multiple onChange={onFilesChange} />
        </label>
        {pdfFiles.length > 0 && (
          <p className="muted">
            Выбрано файлов: {pdfFiles.length}. Общий объём: {formatBytes(pdfFiles.reduce((acc, f) => acc + f.size, 0))}.
          </p>
        )}
        <button type="submit" disabled={loading || pdfFiles.length === 0}>
          {loading ? "Загружаем..." : "Загрузить комплект"}
        </button>
        <p className="muted">Каждый файл не должен превышать лимит сервера (см. max_upload_mb). До 100 файлов за один запрос. После сохранения считаются CRC32 и выполняется структурная проверка встроенной подписи PDF (УКЭП в составе файла).</p>
        {error && <p className="error">{error}</p>}
      </form>

      <div className="card">
        <h2>Принятый комплект</h2>
        {!bundleResult && <p className="muted">После загрузки здесь появится идентификатор партии и список сохранённых файлов.</p>}
        {bundleResult && (
          <>
            <p>
              <strong>Идентификатор комплекта:</strong> <code className="inline-code">{bundleResult.batch_id}</code>
            </p>
            <p className="muted">Всего файлов: {bundleResult.total_files}</p>
            <p>
              <strong>CRC32 манифеста комплекта:</strong>{" "}
              <code className="inline-code">{bundleResult.bundle_manifest_crc32_hex}</code>
            </p>
            <div className="bundle-block-start">
              <p className="issue-header">
                <span>Сводка по УКЭП (структурно)</span>
                <StatusBadge status={bundleResult.overall_ukep_status} compact />
              </p>
              <p className="muted bundle-path">{bundleResult.ukep_disclaimer}</p>
            </div>
            <ul className="bundle-file-list">
              {bundleResult.files.map((item) => (
                <li key={`${item.relative_path}-${item.original_filename}`}>
                  <div className="issue-header">
                    <span>{item.original_filename}</span>
                    <span>{formatBytes(item.size_bytes)}</span>
                  </div>
                  <p className="muted bundle-path">{item.relative_path}</p>
                  <p className="bundle-meta">
                    <span>
                      CRC32: <code className="inline-code">{item.crc32_hex}</code>
                    </span>
                    <StatusBadge status={item.ukep.status} compact />
                  </p>
                  <dl className="ukep-details">
                    <div className="ukep-details-row">
                      <dt>Подписал</dt>
                      <dd>{item.ukep.signer_full_name ?? "—"}</dd>
                    </div>
                    <div className="ukep-details-row">
                      <dt>Сертификат</dt>
                      <dd
                        className={
                          item.ukep.certificate_valid === true
                            ? "ukep-cert-ok"
                            : item.ukep.certificate_valid === false
                              ? "ukep-cert-bad"
                              : ""
                        }
                      >
                        {formatCertificateValidity(item.ukep)}
                      </dd>
                    </div>
                    <div className="ukep-details-row">
                      <dt>Дата подписания</dt>
                      <dd>{formatSignedAt(item.ukep.signed_at)}</dd>
                    </div>
                    {item.ukep.fz63_summary ? (
                      <div className="ukep-details-row">
                        <dt>63-ФЗ</dt>
                        <dd
                          className={
                            item.ukep.fz63_compliant === true
                              ? "ukep-cert-ok"
                              : item.ukep.fz63_compliant === false
                                ? "ukep-cert-bad"
                                : ""
                          }
                        >
                          {item.ukep.fz63_summary}
                        </dd>
                      </div>
                    ) : null}
                  </dl>
                  {item.ukep.fz63_checks.length > 0 ? (
                    <ul className="fz63-check-list">
                      {item.ukep.fz63_checks.map((check) => (
                        <li
                          key={check.id}
                          className={
                            check.passed === true ? "fz63-ok" : check.passed === false ? "fz63-fail" : "fz63-skip"
                          }
                        >
                          <strong>{check.title}</strong>
                          <span>{check.passed === true ? " ✓" : check.passed === false ? " ✗" : " —"}</span>
                          <p className="muted bundle-path">{check.detail}</p>
                        </li>
                      ))}
                    </ul>
                  ) : null}
                  <p className="muted bundle-path bundle-ukep-line">{item.ukep.message}</p>
                  <p className="muted bundle-path">
                    sigflags: {item.ukep.sig_flags == null ? "—" : String(item.ukep.sig_flags)}, полей подписи (виджеты /Sig):{" "}
                    {item.ukep.signature_widget_count}
                  </p>
                </li>
              ))}
            </ul>
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

function formatSignedAt(iso: string | null): string {
  if (!iso) {
    return "—";
  }
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return iso;
  }
  return date.toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  });
}

function formatCertificateValidity(ukep: BundlePdfUkepValidation): string {
  if (ukep.certificate_valid === true) {
    return "действителен";
  }
  if (ukep.certificate_valid === false) {
    return ukep.certificate_validity_label;
  }
  return ukep.certificate_validity_label || "не определено";
}

function formatBytes(bytes: number): string {
  if (bytes === 0) {
    return "0 Б";
  }
  const units = ["Б", "КБ", "МБ", "ГБ"];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / 1024 ** i;
  const rounded = i === 0 ? value : Math.round(value * 10) / 10;
  return `${rounded} ${units[i]}`;
}

async function extractError(response: Response) {
  try {
    const data = await response.json();
    return typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
  } catch {
    return `HTTP ${response.status}`;
  }
}
