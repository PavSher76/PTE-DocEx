import { type ChangeEvent, FormEvent, useEffect, useState } from "react";

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

type AppRoute = "correspondence" | "documents" | "projectContext" | "learnedLessons";
type DocumentsSubTab = "compare" | "bundleUpload";

type ProjectProfileSummary = {
  id: number;
  project_cipher: string;
  name: string;
  primary_schema_binding: string;
  updated_at: string;
};

type ProjectProfileRead = {
  id: number;
  project_cipher: string;
  name: string;
  description: string;
  primary_schema_binding: string;
  package: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

type InvestmentProjectExportResponse = {
  ai_context_json: string;
  design_assignment_xml: string;
};

type LearnedLessonRootCause = {
  title: string;
  description: string;
  related_lessons: string[];
};

type LearnedLessonsAnalysis = {
  summary: string;
  root_causes: LearnedLessonRootCause[];
  systemic_recommendations: string[];
};

type LearnedLessonsResult = {
  parsed_data: {
    metadata: Record<string, string>;
    summary: { sections_count: number; lessons_count: number };
    lessons: Array<Record<string, string | null>>;
  };
  ollama_prompt: string;
  ollama_model: string;
  analysis: LearnedLessonsAnalysis;
  status: Status;
};

const apiBase = import.meta.env.VITE_API_BASE_URL ?? "";
const defaultLearnedLessonsPrompt =
  "Ты эксперт управления проектами. Рассмотри данные сессии выученные уроки и выяви корневые причины указанных проект в проекте. Дай рекомендации по системному устранению корневых причин.";
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

const defaultHero = {
  eyebrow: "Локальный MVP",
  title: "Контроль исходящей переписки и документации",
  description:
    "Загружайте PDF исходящих писем для проверки через OCR, LanguageTool и Ollama, сравнивайте PDF с редактируемым оригиналом, ведите контекст инвестиционно-строительного проекта для консистентности данных и генерации документов."
};

const routeHero: Partial<Record<AppRoute, typeof defaultHero>> = {
  learnedLessons: {
    eyebrow: "Сессии выученных уроков",
    title: "Выученные уроки с ИИ",
    description:
      "Загрузите форму «Форма для подготовки к сессии ВУ» (.xlsm, .xlsx): система разберёт метаданные проекта, разделы и строки уроков в JSON, затем передаст их в локальную модель Ollama. Выберите модель, при необходимости скорректируйте промпт и получите анализ корневых причин с системными рекомендациями по устранению."
  }
};

function getHeroContent(route: AppRoute) {
  return routeHero[route] ?? defaultHero;
}

export default function App() {
  const [route, setRoute] = useState<AppRoute>("correspondence");
  const hero = getHeroContent(route);

  return (
    <div className="app-frame">
      <aside className="sidebar" aria-label="Основная навигация">
        <div className="sidebar-brand">
          <p className="sidebar-eyebrow">PTE DocEx</p>
          <p className="sidebar-title">Локальный MVP</p>
        </div>
        <nav className="sidebar-nav">
          <button
            type="button"
            className={route === "correspondence" ? "active" : ""}
            onClick={() => setRoute("correspondence")}
          >
            Переписка
          </button>
          <button type="button" className={route === "documents" ? "active" : ""} onClick={() => setRoute("documents")}>
            Документация
          </button>
          <button
            type="button"
            className={route === "projectContext" ? "active" : ""}
            onClick={() => setRoute("projectContext")}
          >
            Контекст проекта
          </button>
          <button
            type="button"
            className={route === "learnedLessons" ? "active" : ""}
            onClick={() => setRoute("learnedLessons")}
          >
            Выученные Уроки с ИИ
          </button>
        </nav>
        <p className="sidebar-foot muted">
          Datacentric-ядро: единый JSON-пакет проекта, экспорт по привязке к XML-схеме (Минстрой «Задание на проектирование» 01.00).
        </p>
      </aside>

      <div className="app-main">
        <div className="app-main-inner">
          <header className="hero">
            <div>
              <p className="eyebrow">{hero.eyebrow}</p>
              <h1>{hero.title}</h1>
              <p>{hero.description}</p>
            </div>
          </header>

          {route === "correspondence" && <CorrespondencePanel />}
          {route === "documents" && <DocumentsPanel />}
          {route === "projectContext" && <ProjectContextPanel />}
          {route === "learnedLessons" && <LearnedLessonsPanel />}
        </div>
      </div>
    </div>
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

function LearnedLessonsPanel() {
  const [excelFile, setExcelFile] = useState<File | null>(null);
  const [analysisPrompt, setAnalysisPrompt] = useState(defaultLearnedLessonsPrompt);
  const [ollamaModels, setOllamaModels] = useState<string[]>([]);
  const [defaultOllamaModel, setDefaultOllamaModel] = useState("");
  const [selectedModel, setSelectedModel] = useState("");
  const [modelsLoading, setModelsLoading] = useState(true);
  const [modelsError, setModelsError] = useState("");
  const [result, setResult] = useState<LearnedLessonsResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadModels() {
      setModelsLoading(true);
      setModelsError("");
      try {
        const response = await fetch(`${apiBase}/api/learned-lessons/models`);
        if (!response.ok) {
          throw new Error(await extractError(response));
        }
        const data = (await response.json()) as {
          models: string[];
          default_model: string;
          ollama_reachable?: boolean;
          error?: string | null;
        };
        if (cancelled) {
          return;
        }
        setOllamaModels(data.models);
        setDefaultOllamaModel(data.default_model);
        setSelectedModel(data.models.includes(data.default_model) ? data.default_model : data.models[0] ?? data.default_model);
        if (data.ollama_reachable === false && data.error) {
          setModelsError(data.error);
        }
      } catch (caught) {
        if (!cancelled) {
          setModelsError(caught instanceof Error ? caught.message : "Не удалось загрузить список моделей Ollama.");
        }
      } finally {
        if (!cancelled) {
          setModelsLoading(false);
        }
      }
    }

    void loadModels();
    return () => {
      cancelled = true;
    };
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!excelFile) {
      return;
    }

    const formData = new FormData();
    formData.append("excel_file", excelFile);
    formData.append("analysis_prompt", analysisPrompt);
    if (selectedModel) {
      formData.append("ollama_model", selectedModel);
    }
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${apiBase}/api/learned-lessons/analyze`, {
        method: "POST",
        body: formData
      });
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      setResult((await response.json()) as LearnedLessonsResult);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Не удалось выполнить анализ.");
    } finally {
      setLoading(false);
    }
  }

  const metadata = result?.parsed_data.metadata;

  return (
    <section className="grid">
      <form className="card" onSubmit={submit}>
        <h2>Выученные уроки с ИИ</h2>
        <p className="muted">
          Загрузите форму «Форма для подготовки к сессии ВУ» (.xlsm, .xlsx). Данные будут разобраны и переданы в Ollama
          для выявления корневых причин и системных рекомендаций.
        </p>
        <label>
          Форма подготовки к сессии ВУ
          <input
            type="file"
            accept=".xlsm,.xlsx,.xls,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            onChange={(event) => setExcelFile(event.target.files?.[0] ?? null)}
            required
          />
        </label>
        <label>
          Модель Ollama
          <select
            value={selectedModel}
            onChange={(event) => setSelectedModel(event.target.value)}
            disabled={modelsLoading || ollamaModels.length === 0}
            required
          >
            {modelsLoading && <option value="">Загрузка моделей…</option>}
            {!modelsLoading && ollamaModels.length === 0 && (
              <option value={defaultOllamaModel || ""}>
                {defaultOllamaModel ? `${defaultOllamaModel} (по умолчанию)` : "Модели не найдены"}
              </option>
            )}
            {ollamaModels.map((model) => (
              <option key={model} value={model}>
                {model}
                {model === defaultOllamaModel ? " (по умолчанию)" : ""}
              </option>
            ))}
          </select>
        </label>
        {modelsError && <p className="error">{modelsError}</p>}
        {!modelsLoading && ollamaModels.length === 0 && !modelsError && (
          <p className="muted">
            Ollama недоступна или локально не установлены модели. Будет использована модель по умолчанию из конфигурации.
          </p>
        )}
        <details className="settings-panel">
          <summary>Промпт для анализа</summary>
          <label>
            Инструкция для Ollama
            <textarea value={analysisPrompt} onChange={(event) => setAnalysisPrompt(event.target.value)} rows={8} required />
          </label>
        </details>
        <button type="submit" disabled={loading || !excelFile || modelsLoading}>
          {loading ? "Разбираем форму и анализируем..." : "Загрузить и проанализировать"}
        </button>
        {error && <p className="error">{error}</p>}
      </form>

      <div className="card">
        <h2>Результат</h2>
        {!result && <p className="muted">Здесь появятся разобранные уроки и выводы ИИ.</p>}
        {result && (
          <>
            <StatusBadge status={result.status} />
            <p className="muted">
              <strong>Модель:</strong> {result.ollama_model}
            </p>
            <section className="result-block">
              <h3>Данные сессии</h3>
              <p>
                <strong>Уроков в форме:</strong> {result.parsed_data.summary.lessons_count} (разделов:{" "}
                {result.parsed_data.summary.sections_count})
              </p>
              {metadata?.project_name && (
                <p>
                  <strong>Проект:</strong> {metadata.project_name}
                </p>
              )}
              {metadata?.documentation_type && (
                <p>
                  <strong>Документация:</strong> {metadata.documentation_type}
                </p>
              )}
              {(metadata?.position || metadata?.responsible_person) && (
                <p>
                  <strong>Ответственный:</strong> {[metadata.position, metadata.responsible_person].filter(Boolean).join(", ")}
                </p>
              )}
              <details>
                <summary>Разобранные уроки ({result.parsed_data.lessons.length})</summary>
                {result.parsed_data.lessons.map((lesson) => (
                  <article className="issue" key={String(lesson.number)}>
                    <div className="issue-header">
                      <strong>
                        {lesson.number}
                        {lesson.violation_type ? ` — ${lesson.violation_type}` : ""}
                      </strong>
                      {lesson.category ? <span>{lesson.category}</span> : null}
                    </div>
                    {lesson.situation && <p className="context">{lesson.situation}</p>}
                    {lesson.root_cause_description && (
                      <p>
                        <strong>Причины:</strong> {lesson.root_cause_description}
                      </p>
                    )}
                  </article>
                ))}
              </details>
            </section>
            <section className="result-block">
              <h3>Анализ ИИ</h3>
              <p>{result.analysis.summary}</p>
              {result.analysis.root_causes.length > 0 && (
                <>
                  <h4>Корневые причины</h4>
                  {result.analysis.root_causes.map((item) => (
                    <article className="issue" key={item.title}>
                      <div className="issue-header">
                        <strong>{item.title}</strong>
                        {item.related_lessons.length > 0 && <span>Уроки: {item.related_lessons.join(", ")}</span>}
                      </div>
                      <p>{item.description}</p>
                    </article>
                  ))}
                </>
              )}
              {result.analysis.systemic_recommendations.length > 0 && (
                <>
                  <h4>Системные рекомендации</h4>
                  <ul>
                    {result.analysis.systemic_recommendations.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </>
              )}
            </section>
            <section className="result-block">
              <h3>Исходные данные</h3>
              <details className="project-context-new-profile-tile">
                <summary>JSON формы ВУ</summary>
                <div className="project-context-new-profile-inner">
                  <pre>{JSON.stringify(result.parsed_data, null, 2)}</pre>
                </div>
              </details>
              <details className="project-context-new-profile-tile">
                <summary>Промпт, отправленный в Ollama</summary>
                <div className="project-context-new-profile-inner">
                  <pre>{result.ollama_prompt}</pre>
                </div>
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

function ProjectContextPanel() {
  const [profiles, setProfiles] = useState<ProjectProfileSummary[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [projectCipherNew, setProjectCipherNew] = useState("");
  const [nameNew, setNameNew] = useState("");
  const [descriptionNew, setDescriptionNew] = useState("");
  const [projectCipherLocked, setProjectCipherLocked] = useState("");
  const [nameInput, setNameInput] = useState("");
  const [descInput, setDescInput] = useState("");
  const [bindingInput, setBindingInput] = useState("design_assignment_01_00");
  const [packageText, setPackageText] = useState("{}");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [exportOut, setExportOut] = useState<InvestmentProjectExportResponse | null>(null);

  async function refreshProfiles() {
    try {
      const response = await fetch(`${apiBase}/api/project-context/profiles`);
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      setProfiles((await response.json()) as ProjectProfileSummary[]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Не удалось загрузить профили.");
    }
  }

  useEffect(() => {
    void refreshProfiles();
  }, []);

  /** Пока редактор пустой (`{}`), подставляем шаблон — иначе POST уходит без assignment. */
  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const response = await fetch(`${apiBase}/api/project-context/package-template`);
        if (!response.ok || cancelled) {
          return;
        }
        const data = await response.json();
        setPackageText((prev) => (prev.trim() === "{}" ? JSON.stringify(data, null, 2) : prev));
      } catch {
        /* пользователь может нажать «Загрузить шаблон» */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (selectedId === null) {
      return;
    }
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError("");
      try {
        const response = await fetch(`${apiBase}/api/project-context/profiles/${selectedId}`);
        if (!response.ok) {
          throw new Error(await extractError(response));
        }
        const data = (await response.json()) as ProjectProfileRead;
        if (cancelled) {
          return;
        }
        setProjectCipherLocked(data.project_cipher);
        setNameInput(data.name);
        setDescInput(data.description);
        setBindingInput(data.primary_schema_binding);
        setPackageText(JSON.stringify(data.package, null, 2));
        setExportOut(null);
      } catch (caught) {
        if (!cancelled) {
          setError(caught instanceof Error ? caught.message : "Ошибка загрузки профиля.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [selectedId]);

  async function loadTemplate() {
    setError("");
    try {
      const response = await fetch(`${apiBase}/api/project-context/package-template`);
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      const data = await response.json();
      setPackageText(JSON.stringify(data, null, 2));
      setExportOut(null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Не удалось загрузить шаблон.");
    }
  }

  async function createProfile(event: FormEvent) {
    event.preventDefault();
    setError("");
    let pkg: Record<string, unknown>;
    try {
      pkg = JSON.parse(packageText) as Record<string, unknown>;
    } catch {
      setError("Невалидный JSON пакета.");
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(`${apiBase}/api/project-context/profiles`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_cipher: projectCipherNew.trim(),
          name: nameNew.trim(),
          description: descriptionNew,
          primary_schema_binding: bindingInput,
          package: pkg
        })
      });
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      const created = (await response.json()) as ProjectProfileRead;
      await refreshProfiles();
      setSelectedId(created.id);
      setProjectCipherNew("");
      setNameNew("");
      setDescriptionNew("");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Не удалось создать профиль.");
    } finally {
      setLoading(false);
    }
  }

  async function saveProfile(event: FormEvent) {
    event.preventDefault();
    if (selectedId === null) {
      setError("Выберите сохранённый профиль для обновления.");
      return;
    }
    setError("");
    let pkg: Record<string, unknown>;
    try {
      pkg = JSON.parse(packageText) as Record<string, unknown>;
    } catch {
      setError("Невалидный JSON пакета.");
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(`${apiBase}/api/project-context/profiles/${selectedId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: nameInput,
          description: descInput,
          primary_schema_binding: bindingInput,
          package: pkg
        })
      });
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      await refreshProfiles();
      setExportOut(null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Не удалось сохранить.");
    } finally {
      setLoading(false);
    }
  }

  async function exportFromEditor() {
    setError("");
    let pkg: Record<string, unknown>;
    try {
      pkg = JSON.parse(packageText) as Record<string, unknown>;
    } catch {
      setError("Невалидный JSON пакета.");
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(`${apiBase}/api/project-context/export`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(pkg)
      });
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      setExportOut((await response.json()) as InvestmentProjectExportResponse);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Экспорт не выполнен.");
    } finally {
      setLoading(false);
    }
  }

  async function exportSelectedProfile() {
    if (selectedId === null) {
      setError("Выберите профиль.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const response = await fetch(`${apiBase}/api/project-context/profiles/${selectedId}/export`, {
        method: "POST"
      });
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      setExportOut((await response.json()) as InvestmentProjectExportResponse);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Экспорт не выполнен.");
    } finally {
      setLoading(false);
    }
  }

  async function deleteSelected() {
    if (selectedId === null) {
      return;
    }
    if (!window.confirm("Удалить профиль из базы?")) {
      return;
    }
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${apiBase}/api/project-context/profiles/${selectedId}`, { method: "DELETE" });
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      setSelectedId(null);
      setPackageText("{}");
      await refreshProfiles();
      setExportOut(null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Не удалось удалить.");
    } finally {
      setLoading(false);
    }
  }

  function downloadXml() {
    if (!exportOut) {
      return;
    }
    const blob = new Blob([exportOut.design_assignment_xml], { type: "application/xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "design-assignment.xml";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section className="project-context-layout">
      <div className="card project-context-intro">
        <h2>Контекст проекта</h2>
        <p className="muted doc-lede">
          Единый JSON-пакет (<code className="inline-code">InvestmentProjectPackage</code>) хранится в SQLite как источник правды для последующих проверок консистентности и генерации XML по привязке{" "}
          <code className="inline-code">primary_schema_binding</code> (сейчас поддерживается{" "}
          <code className="inline-code">design_assignment_01_00</code> → Минстрой DesignAssignment-01-00.xsd). Профиль в базе идентифицируется{" "}
          <strong>шифром проекта</strong> (уникальная строка вроде <code className="inline-code">3D01-0036-ТУГН.24.2144У-П-01</code>).
        </p>
        {error && <p className="error">{error}</p>}
      </div>

      <div className="grid project-context-grid">
        <div className="card">
          <h3>Профили</h3>
          <label>
            Выбор профиля
            <select
              value={selectedId ?? ""}
              onChange={(e) => setSelectedId(e.target.value === "" ? null : Number(e.target.value))}
            >
              <option value="">— не выбран —</option>
              {profiles.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.project_cipher} — {p.name}
                </option>
              ))}
            </select>
          </label>
          {selectedId !== null && (
            <p className="muted">
              Шифр проекта: <code className="inline-code">{projectCipherLocked}</code>, обновлён{" "}
              {new Date(profiles.find((x) => x.id === selectedId)?.updated_at ?? "").toLocaleString("ru-RU")}
            </p>
          )}
          <details className="project-context-new-profile-tile">
            <summary>Новый профиль</summary>
            <div className="project-context-new-profile-inner">
              <form onSubmit={createProfile} className="stack-form">
                <label>
                  Шифр проекта (например 3D01-0036-ТУГН.24.2144У-П-01)
                  <input
                    value={projectCipherNew}
                    onChange={(e) => setProjectCipherNew(e.target.value)}
                    placeholder="3D01-0036-ТУГН.24.2144У-П-01"
                    required
                  />
                </label>
                <label>
                  Название
                  <input value={nameNew} onChange={(e) => setNameNew(e.target.value)} placeholder="Демо-проект" required />
                </label>
                <label>
                  Описание (новый профиль)
                  <textarea value={descriptionNew} onChange={(e) => setDescriptionNew(e.target.value)} rows={2} />
                </label>
                <button type="submit" disabled={loading}>
                  Создать профиль
                </button>
              </form>
            </div>
          </details>
          {selectedId !== null && (
            <button type="button" className="danger-outline" onClick={() => void deleteSelected()} disabled={loading}>
              Удалить выбранный
            </button>
          )}
        </div>

        <div className="card">
          <h3>Пакет данных (JSON)</h3>
          <div className="button-row">
            <button type="button" onClick={() => void loadTemplate()} disabled={loading}>
              Загрузить шаблон с сервера
            </button>
            <button type="button" onClick={() => void exportFromEditor()} disabled={loading}>
              Экспорт из редактора (без сохранения)
            </button>
            <button type="button" onClick={() => void exportSelectedProfile()} disabled={loading || selectedId === null}>
              Экспорт выбранного профиля
            </button>
            <button type="button" onClick={() => downloadXml()} disabled={!exportOut}>
              Скачать XML
            </button>
          </div>
          <form onSubmit={saveProfile} className="stack-form">
            <label>
              Наименование (редактируемое)
              <input value={nameInput} onChange={(e) => setNameInput(e.target.value)} />
            </label>
            <label>
              Описание
              <textarea value={descInput} onChange={(e) => setDescInput(e.target.value)} rows={2} />
            </label>
            <label>
              Привязка схемы
              <input value={bindingInput} onChange={(e) => setBindingInput(e.target.value)} />
            </label>
            <label>
              JSON (<code className="inline-code">narratives</code> + <code className="inline-code">assignment</code>)
              <textarea className="mono-editor" value={packageText} onChange={(e) => setPackageText(e.target.value)} rows={22} spellCheck={false} />
            </label>
            <button type="submit" disabled={loading || selectedId === null}>
              Сохранить в базу
            </button>
          </form>

          {exportOut && (
            <div className="export-preview">
              <h4>Результат экспорта</h4>
              <details>
                <summary>Контекст для LLM (JSON)</summary>
                <pre className="text-preview">{exportOut.ai_context_json}</pre>
              </details>
              <details>
                <summary>XML (фрагмент)</summary>
                <pre className="text-preview">{exportOut.design_assignment_xml.slice(0, 4000)}
                  {exportOut.design_assignment_xml.length > 4000 ? "\n…" : ""}
                </pre>
              </details>
            </div>
          )}
        </div>
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
