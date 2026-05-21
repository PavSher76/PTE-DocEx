import { type ChangeEvent, FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { IsmDocumentsModule } from "./IsmDocumentsModule";

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

type RagIngestSummary = {
  enabled: boolean;
  status: string;
  project_id?: string | null;
  collection_label: string;
  collection_name: string;
  documents_queued: number;
  documents_failed: number;
  message: string;
};

type BundleListItem = {
  batch_id: string;
  project_cipher: string | null;
  total_files: number;
  created_at: string;
  overall_ukep_status: Status;
  pipeline_status: string;
  pipeline_label: string;
  rag_project_id: string | null;
};

type BundlePipelineFileStatus = {
  filename: string;
  document_id: string | null;
  job_status: string;
  job_stage: string | null;
  tokens_count: number;
  error: string | null;
};

type BundleDetail = {
  batch_id: string;
  project_cipher: string | null;
  total_files: number;
  created_at: string;
  overall_ukep_status: Status;
  bundle_manifest_crc32_hex: string;
  pipeline_status: string;
  pipeline_label: string;
  files: BundlePdfUploadItem[];
  rag_ingest: RagIngestSummary | null;
  pipeline_files: BundlePipelineFileStatus[];
};

type BundleContextExcerpt = {
  text: string;
  source: "token" | "search";
  document_id: string | null;
  filename: string | null;
  page_number: number | null;
  element_type: string | null;
  discipline: string | null;
  document_code: string | null;
  score: number | null;
};

type BundleContextDocumentSummary = {
  document_id: string;
  filename: string;
  job_status: string;
  tokens_count: number;
  tokens_sampled: number;
  disciplines: string[];
  document_codes: string[];
};

type BundleContextStructured = {
  batch_id: string;
  project_cipher: string | null;
  rag_project_id: string | null;
  collection_label: string;
  pipeline_status: string;
  pipeline_label: string;
  documents_indexed: number;
  documents_total: number;
  total_tokens: number;
  disciplines: string[];
  document_codes: string[];
  element_types: Record<string, number>;
  documents: BundleContextDocumentSummary[];
  ntd_refs: string[];
};

type BundleProjectContext = {
  batch_id: string;
  status: "ready" | "partial" | "unavailable";
  built_at: string;
  summary: string;
  structured: BundleContextStructured;
  excerpts: BundleContextExcerpt[];
  ai_context_json: string;
  message: string;
};

type DocumentBundleUploadResponse = {
  batch_id: string;
  project_cipher?: string | null;
  total_files: number;
  files: BundlePdfUploadItem[];
  bundle_manifest_crc32_hex: string;
  overall_ukep_status: Status;
  ukep_disclaimer: string;
  rag_ingest?: RagIngestSummary | null;
};

type AppRoute =
  | "correspondence"
  | "documents"
  | "projectContext"
  | "projectAnalysis"
  | "ismDocuments"
  | "learnedLessons";


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

type ProjectContextChatTurn = {
  role: "user" | "assistant";
  content: string;
};

type ProjectContextChatResponse = {
  reply: string;
  changes_summary: string;
  suggested_package: Record<string, unknown> | null;
  package_valid: boolean;
  ollama_model: string;
  ollama_prompt: string;
};

type ProjectContextDocumentIngestResponse = {
  filename: string;
  extracted_text: string;
  char_count: number;
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
const defaultProjectContextChatPrompt =
  "Ты помощник по datacentric-контексту инвестиционно-строительного проекта. Дополняй narratives и assignment фактами из документа и диалога; не выдумывай реквизиты и коды без источника.";

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
  eyebrow: "Гипотезы применения ИИ в Инжиниринге",
  title: "Контроль исходящей переписки и документации",
  description:
    "Загружайте PDF исходящих писем для проверки через OCR, LanguageTool и Ollama, сравнивайте PDF с редактируемым оригиналом, ведите контекст инвестиционно-строительного проекта для консистентности данных и генерации документов."
};

const routeHero: Partial<Record<AppRoute, typeof defaultHero>> = {
  projectContext: {
    eyebrow: "Datacentric-ядро",
    title: "Контекст проекта",
    description:
      "Выберите профиль по шифру проекта, загрузите исходный документ (PDF, DOCX, ODT, RTF или TXT) и обсудите данные с локальной Ollama. ИИ предложит обновлённый JSON-пакет InvestmentProjectPackage — примените его к контексту и сохраните для экспорта в LLM и XML «Задание на проектирование»."
  },
  learnedLessons: {
    eyebrow: "Сессии выученных уроков",
    title: "Выученные уроки с ИИ",
    description:
      "Загрузите форму «Форма для подготовки к сессии ВУ» (.xlsm, .xlsx): система разберёт метаданные проекта, разделы и строки уроков в JSON, затем передаст их в локальную модель Ollama. Выберите модель, при необходимости скорректируйте промпт и получите анализ корневых причин с системными рекомендациями по устранению."
  },
  projectAnalysis: {
    eyebrow: "ПД / РД",
    title: "Анализ проекта",
    description:
      "Пакетная загрузка комплекта PDF (тома и листы ПД или РД): приёмка на сервер, CRC32 манифеста, структурная проверка встроенной УКЭП. Укажите шифр проекта для привязки партии."
  },
  ismDocuments: {
    eyebrow: "ИСМ",
    title: "Документы ИСМ",
    description:
      "Пакетная загрузка документов инженерно-сметной модели (DOC, XLS, PDF): извлечение структурированного контекста, выявление междисциплинарных связей и индексация в RAG."
  }
};

function getHeroContent(route: AppRoute) {
  return routeHero[route] ?? defaultHero;
}

export default function App() {
  const [route, setRoute] = useState<AppRoute>("correspondence");
  const inProgressActive =
    route === "documents" ||
    route === "projectContext" ||
    route === "projectAnalysis" ||
    route === "ismDocuments";
  const [inProgressOpen, setInProgressOpen] = useState(inProgressActive);
  const hero = getHeroContent(route);

  useEffect(() => {
    if (inProgressActive) {
      setInProgressOpen(true);
    }
  }, [inProgressActive]);

  useEffect(() => {
    if (route === "ismDocuments" && !window.location.hash.includes("ism-documents")) {
      window.location.hash = "#/ism-documents/registry";
    }
  }, [route]);

  return (
    <div className="app-frame">
      <aside className="sidebar" aria-label="Основная навигация">
        <div className="sidebar-brand">
          <p className="sidebar-eyebrow">PTE AI-Engineering</p>
          <p className="sidebar-title">Гипотезы применения ИИ в Инжиниринге</p>
        </div>
        <nav className="sidebar-nav">
          <button
            type="button"
            className={route === "correspondence" ? "active" : ""}
            onClick={() => setRoute("correspondence")}
          >
            Переписка
          </button>
          <button
            type="button"
            className={route === "learnedLessons" ? "active" : ""}
            onClick={() => setRoute("learnedLessons")}
          >
            Выученные Уроки с ИИ
          </button>
          <div className="sidebar-group">
            <button
              type="button"
              className={`sidebar-group-toggle ${inProgressOpen ? "open" : ""} ${inProgressActive ? "active" : ""}`}
              aria-expanded={inProgressOpen}
              onClick={() => setInProgressOpen((open) => !open)}
            >
              В работе
            </button>
            {inProgressOpen && (
              <div className="sidebar-subnav">
                <button
                  type="button"
                  className={route === "documents" ? "active" : ""}
                  onClick={() => setRoute("documents")}
                >
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
                  className={route === "projectAnalysis" ? "active" : ""}
                  onClick={() => setRoute("projectAnalysis")}
                >
                  Анализ проекта
                </button>
                <button
                  type="button"
                  className={route === "ismDocuments" ? "active" : ""}
                  onClick={() => setRoute("ismDocuments")}
                >
                  Документы ИСМ
                </button>
              </div>
            )}
          </div>
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
          {route === "projectAnalysis" && <ProjectAnalysisPanel />}
          {route === "ismDocuments" && <IsmDocumentsModule />}
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
          setModelsError(
            caught instanceof Error ? caught.message : "Не удалось загрузить список моделей Ollama."
          );
          setDefaultOllamaModel((prev) => prev || "llama3.1:8b");
          setSelectedModel((prev) => prev || "llama3.1:8b");
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

  const effectiveModel = selectedModel || defaultOllamaModel;

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!excelFile) {
      return;
    }

    const formData = new FormData();
    formData.append("excel_file", excelFile);
    formData.append("analysis_prompt", analysisPrompt);
    if (effectiveModel) {
      formData.append("ollama_model", effectiveModel);
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
            value={effectiveModel}
            onChange={(event) => setSelectedModel(event.target.value)}
            disabled={modelsLoading}
          >
            {modelsLoading && <option value="">Загрузка моделей…</option>}
            {!modelsLoading && ollamaModels.length === 0 && effectiveModel && (
              <option value={effectiveModel}>
                {effectiveModel} (из конфигурации сервера)
              </option>
            )}
            {!modelsLoading && ollamaModels.length === 0 && !effectiveModel && (
              <option value="">Модели не найдены</option>
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
        {!modelsLoading && ollamaModels.length === 0 && !modelsError && effectiveModel && (
          <p className="muted">
            Список моделей с Ollama не получен — будет использована модель из конфигурации сервера (
            {effectiveModel}).
          </p>
        )}
        {!modelsLoading && ollamaModels.length === 0 && !modelsError && !effectiveModel && (
          <p className="muted">
            Ollama недоступна или локально не установлены модели. Запустите Ollama на хосте и проверьте
            OLLAMA_BASE_URL.
          </p>
        )}
        <details className="settings-panel">
          <summary>Промпт для анализа</summary>
          <label>
            Инструкция для Ollama
            <textarea value={analysisPrompt} onChange={(event) => setAnalysisPrompt(event.target.value)} rows={8} required />
          </label>
        </details>
        <button type="submit" disabled={loading || !excelFile || modelsLoading || !effectiveModel}>
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
  return <DocumentsCompareSection />;
}

function ProjectAnalysisPanel() {
  const [dashboardKey, setDashboardKey] = useState(0);
  const [selectedBatchId, setSelectedBatchId] = useState<string | null>(null);

  return (
    <div className="grid project-context-grid">
      <BundleDashboard
        refreshKey={dashboardKey}
        selectedBatchId={selectedBatchId}
        onSelectBatch={setSelectedBatchId}
      />
      {selectedBatchId && (
        <BundleDetailPanel
          batchId={selectedBatchId}
          onClose={() => setSelectedBatchId(null)}
          onDeleted={() => {
            setSelectedBatchId(null);
            setDashboardKey((k) => k + 1);
          }}
        />
      )}
      <DocumentBundleUploadSection
        onUploaded={(batchId) => {
          setDashboardKey((k) => k + 1);
          setSelectedBatchId(batchId);
        }}
      />
    </div>
  );
}

function BundleDashboard({
  refreshKey,
  selectedBatchId,
  onSelectBatch
}: {
  refreshKey: number;
  selectedBatchId: string | null;
  onSelectBatch: (batchId: string | null) => void;
}) {
  const [bundles, setBundles] = useState<BundleListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      const response = await fetch(`${apiBase}/api/documents/bundles`);
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      setBundles((await response.json()) as BundleListItem[]);
      setError("");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Не удалось загрузить дашборд.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  useEffect(() => {
    const needsPoll = bundles.some((b) =>
      ["queued", "processing", "partial"].includes(b.pipeline_status)
    );
    if (!needsPoll) {
      return;
    }
    const timer = window.setInterval(() => void load(), 8000);
    return () => window.clearInterval(timer);
  }, [bundles, load]);

  return (
    <section className="card span-wide bundle-dashboard">
      <div className="bundle-dashboard-header">
        <div>
          <h2>Дашборд комплектов</h2>
          <p className="muted doc-lede">
            Ранее загруженные пакеты ПД/РД и статус конвейера RAG (парсинг → токенизация → индексация в коллекцию «Анализ проекта»).
          </p>
        </div>
        <button type="button" className="text-button" onClick={() => void load()} disabled={loading}>
          Обновить
        </button>
      </div>
      {error && <p className="error">{error}</p>}
      {loading && bundles.length === 0 && <p className="muted">Загрузка…</p>}
      {!loading && bundles.length === 0 && !error && (
        <p className="muted">Комплекты ещё не загружались. Используйте форму ниже.</p>
      )}
      {bundles.length > 0 && (
        <div className="bundle-dashboard-table-wrap">
          <table className="bundle-dashboard-table">
            <thead>
              <tr>
                <th>Дата</th>
                <th>Шифр / ID</th>
                <th>Файлов</th>
                <th>УКЭП</th>
                <th>Конвейер RAG</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {bundles.map((row) => (
                <tr key={row.batch_id} className={selectedBatchId === row.batch_id ? "selected" : ""}>
                  <td>{formatDateTime(row.created_at)}</td>
                  <td>
                    {row.project_cipher ? (
                      <code className="inline-code">{row.project_cipher}</code>
                    ) : (
                      <code className="inline-code">{row.batch_id.slice(0, 12)}…</code>
                    )}
                  </td>
                  <td>{row.total_files}</td>
                  <td>
                    <StatusBadge status={row.overall_ukep_status} compact />
                  </td>
                  <td>
                    <PipelineStatusBadge status={row.pipeline_status} label={row.pipeline_label} />
                  </td>
                  <td>
                    <button
                      type="button"
                      className="text-button"
                      onClick={() =>
                        onSelectBatch(selectedBatchId === row.batch_id ? null : row.batch_id)
                      }
                    >
                      {selectedBatchId === row.batch_id ? "Свернуть" : "Подробнее"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function BundleProjectContextModal({
  context,
  onClose,
  onRebuild,
  rebuilding
}: {
  context: BundleProjectContext;
  onClose: () => void;
  onRebuild: () => void;
  rebuilding: boolean;
}) {
  const { structured: s } = context;
  const statusLabels: Record<BundleProjectContext["status"], string> = {
    ready: "Готов",
    partial: "Частично",
    unavailable: "Недоступен"
  };

  const copyAiContext = async () => {
    try {
      await navigator.clipboard.writeText(context.ai_context_json);
    } catch {
      window.prompt("Скопируйте JSON для LLM:", context.ai_context_json);
    }
  };

  return (
    <div
      className="bundle-context-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="bundle-context-title"
      onClick={(event) => {
        if (event.target === event.currentTarget) {
          onClose();
        }
      }}
    >
      <div className="bundle-context-dialog card" onClick={(event) => event.stopPropagation()}>
        <div className="bundle-dashboard-header">
          <h2 id="bundle-context-title">Проектный контекст</h2>
          <div className="button-row">
            <button type="button" className="text-button" onClick={() => void copyAiContext()}>
              Копировать JSON для LLM
            </button>
            <button type="button" className="text-button" onClick={() => void onRebuild()} disabled={rebuilding}>
              {rebuilding ? "Пересборка…" : "Пересобрать"}
            </button>
            <button type="button" className="text-button" onClick={onClose}>
              Закрыть
            </button>
          </div>
        </div>
        <p className="issue-header bundle-context-meta">
          {s.project_cipher && (
            <>
              <strong>Шифр:</strong> <code className="inline-code">{s.project_cipher}</code>
              {" · "}
            </>
          )}
          <span className={`pipeline-badge pipeline-badge--${context.status === "ready" ? "indexed" : context.status}`}>
            {statusLabels[context.status]}
          </span>
          {" · "}
          <span className="muted">Собран: {formatDateTime(context.built_at)}</span>
        </p>
        {context.message && <p className="muted">{context.message}</p>}
        <div className="bundle-context-stats">
          <p>
            <strong>Документов в индексе:</strong> {s.documents_indexed} / {s.documents_total}
          </p>
          <p>
            <strong>Токенов:</strong> {s.total_tokens}
          </p>
          {s.disciplines.length > 0 && (
            <p>
              <strong>Дисциплины:</strong> {s.disciplines.join(", ")}
            </p>
          )}
          {s.document_codes.length > 0 && (
            <p>
              <strong>Коды документов:</strong> {s.document_codes.join(", ")}
            </p>
          )}
          {s.ntd_refs.length > 0 && (
            <p>
              <strong>НТД:</strong> {s.ntd_refs.slice(0, 12).join("; ")}
              {s.ntd_refs.length > 12 ? ` … (+${s.ntd_refs.length - 12})` : ""}
            </p>
          )}
        </div>
        {context.summary && (
          <div className="bundle-context-summary">
            <h3>Краткое содержание</h3>
            <p>{context.summary}</p>
          </div>
        )}
        {s.documents.length > 0 && (
          <>
            <h3>Документы в контексте</h3>
            <div className="bundle-dashboard-table-wrap">
              <table className="bundle-dashboard-table">
                <thead>
                  <tr>
                    <th>Файл</th>
                    <th>Токенов</th>
                    <th>В выборке</th>
                    <th>Дисциплины</th>
                  </tr>
                </thead>
                <tbody>
                  {s.documents.map((doc) => (
                    <tr key={doc.document_id}>
                      <td>{doc.filename}</td>
                      <td>{doc.tokens_count}</td>
                      <td>{doc.tokens_sampled}</td>
                      <td className="muted">{doc.disciplines.join(", ") || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
        {context.excerpts.length > 0 && (
          <>
            <h3>Выдержки ({context.excerpts.length})</h3>
            <ul className="bundle-context-excerpts">
              {context.excerpts.map((excerpt, index) => (
                <li key={`${excerpt.document_id ?? "x"}-${index}`}>
                  <p className="bundle-context-excerpt-meta muted">
                    {excerpt.filename ?? "Документ"}
                    {excerpt.page_number != null ? ` · стр. ${excerpt.page_number}` : ""}
                    {excerpt.discipline ? ` · ${excerpt.discipline}` : ""}
                    {excerpt.document_code ? ` · ${excerpt.document_code}` : ""}
                    {excerpt.element_type ? ` · ${excerpt.element_type}` : ""}
                    {excerpt.source === "search" ? " · поиск" : ""}
                  </p>
                  <p className="bundle-context-excerpt-text">{excerpt.text}</p>
                </li>
              ))}
            </ul>
          </>
        )}
        <details className="bundle-context-json-details">
          <summary>Контекст для LLM (JSON)</summary>
          <pre className="text-preview">{context.ai_context_json}</pre>
        </details>
      </div>
    </div>
  );
}

function BundleDetailPanel({
  batchId,
  onClose,
  onDeleted
}: {
  batchId: string;
  onClose: () => void;
  onDeleted: () => void;
}) {
  const [detail, setDetail] = useState<BundleDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [retrying, setRetrying] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [contextOpen, setContextOpen] = useState(false);
  const [contextData, setContextData] = useState<BundleProjectContext | null>(null);
  const [contextLoading, setContextLoading] = useState(false);
  const [contextRebuilding, setContextRebuilding] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiBase}/api/documents/bundles/${batchId}`);
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      setDetail((await response.json()) as BundleDetail);
      setError("");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Не удалось загрузить детали.");
    } finally {
      setLoading(false);
    }
  }, [batchId]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (!detail || !["queued", "processing", "partial"].includes(detail.pipeline_status)) {
      return;
    }
    const timer = window.setInterval(() => void load(), 8000);
    return () => window.clearInterval(timer);
  }, [detail, load]);

  const retryRag = async () => {
    setRetrying(true);
    setError("");
    try {
      const response = await fetch(`${apiBase}/api/documents/bundles/${batchId}/rag/retry`, {
        method: "POST"
      });
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      await load();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Не удалось перезапустить RAG.");
    } finally {
      setRetrying(false);
    }
  };

  const showRagRetry =
    detail?.pipeline_status === "rag_failed" ||
    detail?.rag_ingest?.status === "failed" ||
    detail?.rag_ingest?.status === "partial";

  const hasIndexedMaterial =
    !!detail &&
    (detail.pipeline_files.some((f) => f.job_status === "indexed" || f.tokens_count > 0) ||
      ["indexed", "partial"].includes(detail.pipeline_status));

  const fetchProjectContext = async (rebuild: boolean) => {
    const setBusy = rebuild ? setContextRebuilding : setContextLoading;
    setBusy(true);
    setError("");
    try {
      let response = await fetch(`${apiBase}/api/documents/bundles/${batchId}/context`);
      if (rebuild || response.status === 404) {
        response = await fetch(`${apiBase}/api/documents/bundles/${batchId}/context/build`, {
          method: "POST"
        });
      }
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      const payload = (await response.json()) as BundleProjectContext;
      setContextData(payload);
      setContextOpen(true);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Не удалось получить проектный контекст.");
    } finally {
      setBusy(false);
    }
  };

  const deleteBundle = async () => {
    const label = detail?.project_cipher?.trim() || batchId;
    if (
      !window.confirm(
        `Удалить комплект «${label}»?\n\nБудут удалены: PDF и метаданные на сервере, документы и векторы в коллекции RAG «Анализ проекта».`
      )
    ) {
      return;
    }
    setDeleting(true);
    setError("");
    try {
      const response = await fetch(`${apiBase}/api/documents/bundles/${batchId}`, {
        method: "DELETE"
      });
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      const payload = (await response.json()) as {
        rag?: { documents_deleted?: number; documents_requested?: number; message?: string };
      };
      const rag = payload.rag;
      if (
        rag &&
        rag.documents_requested &&
        rag.documents_requested > 0 &&
        (rag.documents_deleted ?? 0) < rag.documents_requested
      ) {
        window.alert(
          rag.message ||
            `Комплект удалён локально. В RAG удалено ${rag.documents_deleted ?? 0} из ${rag.documents_requested} документов.`
        );
      }
      onDeleted();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Не удалось удалить комплект.");
    } finally {
      setDeleting(false);
    }
  };

  return (
    <section className="card span-wide bundle-detail-panel">
      <div className="bundle-dashboard-header">
        <h2>Детали комплекта</h2>
        <div className="button-row">
          {hasIndexedMaterial && (
            <button
              type="button"
              className="text-button bundle-context-open-button"
              onClick={() => void fetchProjectContext(false)}
              disabled={contextLoading || loading}
              title="Собрать и показать контекст из проиндексированных материалов RAG"
            >
              {contextLoading ? "Сбор контекста…" : "Проектный контекст"}
            </button>
          )}
          {showRagRetry && (
            <button
              type="button"
              className="text-button"
              onClick={() => void retryRag()}
              disabled={retrying || loading}
            >
              {retrying ? "Отправка в RAG…" : "Перезапустить RAG"}
            </button>
          )}
          <button type="button" className="text-button" onClick={() => void load()} disabled={loading}>
            Обновить статус
          </button>
          <button type="button" className="text-button" onClick={onClose}>
            Закрыть
          </button>
          <button
            type="button"
            className="text-button bundle-delete-button"
            onClick={() => void deleteBundle()}
            disabled={deleting || loading}
          >
            {deleting ? "Удаление…" : "Удалить"}
          </button>
        </div>
      </div>
      {error && <p className="error">{error}</p>}
      {loading && !detail && <p className="muted">Загрузка…</p>}
      {detail && (
        <>
          <p className="muted">
            <strong>ID:</strong> <code className="inline-code">{detail.batch_id}</code>
            {detail.project_cipher && (
              <>
                {" · "}
                <strong>Шифр:</strong> <code className="inline-code">{detail.project_cipher}</code>
              </>
            )}
            {" · "}
            {formatDateTime(detail.created_at)}
          </p>
          <p className="issue-header">
            <span>Конвейер</span>
            <PipelineStatusBadge status={detail.pipeline_status} label={detail.pipeline_label} />
            <StatusBadge status={detail.overall_ukep_status} compact />
          </p>
          {detail.rag_ingest && (
            <div className="rag-ingest-block bundle-block-start">
              <p className="muted">{detail.rag_ingest.message}</p>
              {detail.rag_ingest.project_id && (
                <p className="muted bundle-path">
                  RAG: <code className="inline-code">{detail.rag_ingest.project_id}</code> →{" "}
                  <code className="inline-code">{detail.rag_ingest.collection_name}</code>
                </p>
              )}
            </div>
          )}
          <h3>Статус обработки по файлам</h3>
          <div className="bundle-dashboard-table-wrap">
            <table className="bundle-dashboard-table">
              <thead>
                <tr>
                  <th>Файл</th>
                  <th>Этап</th>
                  <th>Токенов</th>
                  <th>Примечание</th>
                </tr>
              </thead>
              <tbody>
                {(detail.pipeline_files.length > 0
                  ? detail.pipeline_files
                  : detail.files.map((f) => ({
                      filename: f.original_filename,
                      document_id: null,
                      job_status: "accepted",
                      job_stage: null,
                      tokens_count: 0,
                      error: null
                    }))
                ).map((file) => (
                  <tr key={file.filename}>
                    <td>{file.filename}</td>
                    <td>
                      <JobStatusLabel status={file.job_status} stage={file.job_stage} />
                    </td>
                    <td>{file.tokens_count > 0 ? file.tokens_count : "—"}</td>
                    <td className="muted">{file.error ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {detail.files.length > 0 && (
            <details className="bundle-detail-files">
              <summary>УКЭП и CRC32 по файлам ({detail.files.length})</summary>
              <ul className="bundle-file-list">
                {detail.files.map((item) => (
                  <li key={item.relative_path}>
                    <div className="issue-header">
                      <span>{item.original_filename}</span>
                      <StatusBadge status={item.ukep.status} compact />
                    </div>
                    <p className="muted bundle-meta">
                      CRC32: <code className="inline-code">{item.crc32_hex}</code> · {formatBytes(item.size_bytes)}
                    </p>
                  </li>
                ))}
              </ul>
            </details>
          )}
        </>
      )}
      {contextOpen && contextData && (
        <BundleProjectContextModal
          context={contextData}
          onClose={() => setContextOpen(false)}
          onRebuild={() => void fetchProjectContext(true)}
          rebuilding={contextRebuilding}
        />
      )}
    </section>
  );
}

function PipelineStatusBadge({ status, label }: { status: string; label: string }) {
  return <span className={`pipeline-badge pipeline-badge--${status}`}>{label}</span>;
}

function JobStatusLabel({ status, stage }: { status: string; stage: string | null }) {
  const labels: Record<string, string> = {
    uploaded: "Загружен",
    parsing: "Парсинг",
    tokenizing: "Токенизация",
    embedding: "Векторизация",
    indexed: "Индексирован",
    failed: "Ошибка",
    missing: "Нет в RAG",
    accepted: "Принят",
    unknown: "Неизвестно",
    queued: "В очереди"
  };
  const text = labels[status] ?? status;
  return (
    <span>
      {text}
      {stage ? <span className="muted"> ({stage})</span> : null}
    </span>
  );
}

function formatDateTime(iso: string): string {
  try {
    return new Date(iso).toLocaleString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  } catch {
    return iso;
  }
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

function isPdfFile(file: File): boolean {
  return file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
}

function collectPdfFiles(list: FileList | File[] | null): File[] {
  if (!list) {
    return [];
  }
  const arr = Array.isArray(list) ? list : Array.from(list);
  return arr.filter(isPdfFile);
}

function DocumentBundleUploadSection({ onUploaded }: { onUploaded?: (batchId: string) => void }) {
  const [pdfFiles, setPdfFiles] = useState<File[]>([]);
  const [projectCipher, setProjectCipher] = useState("");
  const [bundleResult, setBundleResult] = useState<DocumentBundleUploadResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const folderInputRef = useRef<HTMLInputElement>(null);

  function mergeFiles(incoming: File[]) {
    const pdfs = incoming.filter(isPdfFile);
    if (pdfs.length === 0) {
      setError("Не выбрано ни одного PDF. Поддерживаются только файлы .pdf.");
      return;
    }
    setError("");
    setBundleResult(null);
    setPdfFiles((prev) => {
      const seen = new Set(prev.map((f) => `${f.name}:${f.size}`));
      const merged = [...prev];
      for (const file of pdfs) {
        const key = `${file.name}:${file.size}`;
        if (!seen.has(key)) {
          seen.add(key);
          merged.push(file);
        }
      }
      return merged;
    });
  }

  function onFilesChange(event: ChangeEvent<HTMLInputElement>) {
    mergeFiles(collectPdfFiles(event.target.files));
    event.target.value = "";
  }

  function clearSelection() {
    setPdfFiles([]);
    setBundleResult(null);
    setError("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    if (folderInputRef.current) {
      folderInputRef.current.value = "";
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (pdfFiles.length === 0) {
      return;
    }
    if (pdfFiles.length > 100) {
      setError("За один запрос можно загрузить не более 100 PDF.");
      return;
    }

    const formData = new FormData();
    if (projectCipher.trim()) {
      formData.append("project_cipher", projectCipher.trim());
    }
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
      const payload = (await response.json()) as DocumentBundleUploadResponse;
      setBundleResult(payload);
      onUploaded?.(payload.batch_id);
      setPdfFiles([]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Не удалось загрузить комплект.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="grid span-wide">
      <form className="card" onSubmit={submit}>
        <h2>Пакетная загрузка комплекта</h2>
        <p className="muted doc-lede">
          Загрузите тома и листы ПД или РД одной партией. Файлы сохраняются на сервере с общим идентификатором комплекта для дальнейшего анализа и контроля УКЭП.
        </p>
        <label>
          Шифр проекта (необязательно)
          <input
            type="text"
            placeholder="Напр. 3D01-0036-ТУГН.24.2144У-П-01"
            value={projectCipher}
            onChange={(e) => setProjectCipher(e.target.value)}
            disabled={loading}
          />
        </label>
        <label>
          PDF-файлы
          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf,.pdf"
            multiple
            onChange={onFilesChange}
            disabled={loading}
          />
        </label>
        <label>
          Или папка с PDF
          <input
            ref={folderInputRef}
            type="file"
            accept="application/pdf,.pdf"
            multiple
            // @ts-expect-error webkitdirectory — выбор каталога в Chromium/Safari
            webkitdirectory=""
            onChange={onFilesChange}
            disabled={loading}
          />
        </label>
        {pdfFiles.length > 0 && (
          <>
            <p className="muted">
              Выбрано PDF: {pdfFiles.length}. Общий объём:{" "}
              {formatBytes(pdfFiles.reduce((acc, f) => acc + f.size, 0))}.
            </p>
            <ul className="bundle-pick-list">
              {pdfFiles.slice(0, 12).map((f) => (
                <li key={`${f.name}-${f.size}`}>{f.name}</li>
              ))}
              {pdfFiles.length > 12 && <li className="muted">…и ещё {pdfFiles.length - 12}</li>}
            </ul>
            <button type="button" className="text-button" onClick={clearSelection} disabled={loading}>
              Очистить список
            </button>
          </>
        )}
        <button type="submit" disabled={loading || pdfFiles.length === 0}>
          {loading ? `Загружаем ${pdfFiles.length} файл(ов)…` : "Загрузить комплект"}
        </button>
        <p className="muted">До 150 МБ на каждый PDF, не более 100 файлов за один запрос. После сохранения считаются CRC32 и выполняется структурная проверка встроенной подписи PDF (УКЭП в составе файла).</p>
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
            {bundleResult.project_cipher && (
              <p>
                <strong>Шифр проекта:</strong>{" "}
                <code className="inline-code">{bundleResult.project_cipher}</code>
              </p>
            )}
            <p className="muted">Всего файлов: {bundleResult.total_files}</p>
            {bundleResult.rag_ingest?.enabled && (
              <div className="bundle-block-start rag-ingest-block">
                <p className="issue-header">
                  <span>RAG — {bundleResult.rag_ingest.collection_label}</span>
                </p>
                <p className="muted">{bundleResult.rag_ingest.message}</p>
                {bundleResult.rag_ingest.project_id && (
                  <p className="muted bundle-path">
                    Проект RAG: <code className="inline-code">{bundleResult.rag_ingest.project_id}</code>
                    {" · "}
                    коллекция <code className="inline-code">{bundleResult.rag_ingest.collection_name}</code>
                  </p>
                )}
              </div>
            )}
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
  const [chatMessages, setChatMessages] = useState<ProjectContextChatTurn[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatPrompt, setChatPrompt] = useState(defaultProjectContextChatPrompt);
  const [chatLoading, setChatLoading] = useState(false);
  const [documentName, setDocumentName] = useState("");
  const [documentText, setDocumentText] = useState("");
  const [documentLoading, setDocumentLoading] = useState(false);
  const [suggestedPackage, setSuggestedPackage] = useState<Record<string, unknown> | null>(null);
  const [changesSummary, setChangesSummary] = useState("");
  const [ollamaModels, setOllamaModels] = useState<string[]>([]);
  const [defaultOllamaModel, setDefaultOllamaModel] = useState("");
  const [selectedModel, setSelectedModel] = useState("");
  const [modelsLoading, setModelsLoading] = useState(true);
  const [modelsError, setModelsError] = useState("");
  const chatPanelRef = useRef<HTMLDivElement>(null);

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

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      setModelsLoading(true);
      setModelsError("");
      try {
        const response = await fetch(`${apiBase}/api/project-context/models`);
        if (!response.ok) {
          throw new Error(await extractError(response));
        }
        const data = (await response.json()) as {
          models: string[];
          default_model: string;
          error?: string | null;
        };
        if (cancelled) {
          return;
        }
        setOllamaModels(data.models);
        setDefaultOllamaModel(data.default_model);
        setSelectedModel(data.models[0] ?? data.default_model);
        if (data.error) {
          setModelsError(data.error);
        }
      } catch (caught) {
        if (!cancelled) {
          setModelsError(caught instanceof Error ? caught.message : "Не удалось загрузить модели Ollama.");
        }
      } finally {
        if (!cancelled) {
          setModelsLoading(false);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    setChatMessages([]);
    setChatInput("");
    setDocumentName("");
    setDocumentText("");
    setSuggestedPackage(null);
    setChangesSummary("");
  }, [selectedId]);

  useEffect(() => {
    if (selectedId !== null && chatPanelRef.current) {
      chatPanelRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [selectedId]);

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

  async function ingestDocument(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file || selectedId === null) {
      return;
    }
    setDocumentLoading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("document_file", file);
      const response = await fetch(`${apiBase}/api/project-context/profiles/${selectedId}/ingest-document`, {
        method: "POST",
        body: formData
      });
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      const data = (await response.json()) as ProjectContextDocumentIngestResponse;
      setDocumentName(data.filename);
      setDocumentText(data.extracted_text);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Не удалось извлечь текст из документа.");
    } finally {
      setDocumentLoading(false);
    }
  }

  async function sendChat(event: FormEvent) {
    event.preventDefault();
    if (selectedId === null || !chatInput.trim()) {
      return;
    }
    const userText = chatInput.trim();
    setChatInput("");
    setChatLoading(true);
    setError("");
    const nextHistory: ProjectContextChatTurn[] = [...chatMessages, { role: "user", content: userText }];
    setChatMessages(nextHistory);
    try {
      const response = await fetch(`${apiBase}/api/project-context/profiles/${selectedId}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userText,
          history: chatMessages,
          document_text: documentText || null,
          ollama_model: selectedModel,
          chat_prompt: chatPrompt
        })
      });
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      const data = (await response.json()) as ProjectContextChatResponse;
      setChatMessages([...nextHistory, { role: "assistant", content: data.reply }]);
      setChangesSummary(data.changes_summary);
      setSuggestedPackage(data.suggested_package);
    } catch (caught) {
      setChatMessages(nextHistory.slice(0, -1));
      setChatInput(userText);
      setError(caught instanceof Error ? caught.message : "Не удалось отправить сообщение в чат.");
    } finally {
      setChatLoading(false);
    }
  }

  function applySuggestedToEditor() {
    if (!suggestedPackage) {
      return;
    }
    setPackageText(JSON.stringify(suggestedPackage, null, 2));
    setExportOut(null);
  }

  async function applySuggestedAndSave() {
    if (selectedId === null || !suggestedPackage) {
      return;
    }
    setPackageText(JSON.stringify(suggestedPackage, null, 2));
    setExportOut(null);
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${apiBase}/api/project-context/profiles/${selectedId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: nameInput,
          description: descInput,
          primary_schema_binding: bindingInput,
          package: suggestedPackage
        })
      });
      if (!response.ok) {
        throw new Error(await extractError(response));
      }
      await refreshProfiles();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Не удалось сохранить обновлённый контекст.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="project-context-layout">
      <div className="card project-context-intro">
        <h2>Контекст проекта</h2>
        <p className="muted doc-lede">
          Профиль проекта хранит единый JSON-пакет <code className="inline-code">InvestmentProjectPackage</code> (нарративы и формализованное задание). После выбора профиля откройте{" "}
          <strong>чат с ИИ</strong>: загрузите PDF или редактируемый документ, обсудите данные с локальной Ollama и примените предложенные правки к пакету — затем экспортируйте контекст для LLM или XML «Задание на проектирование» (
          <code className="inline-code">design_assignment_01_00</code>).
        </p>
        {error && <p className="error">{error}</p>}
      </div>

      <div className="grid project-context-grid">
        <div className="card project-context-profiles">
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

        {selectedId !== null && (
          <div ref={chatPanelRef} className="card project-context-chat">
            <h3>Чат с ИИ</h3>
            <p className="muted">
              Загрузите документ с исходными данными проекта, задайте вопросы модели и примените предложенный пакет к контексту профиля{" "}
              <code className="inline-code">{projectCipherLocked}</code>.
            </p>
            <label>
              Документ для контекста (PDF, DOCX, ODT, RTF, TXT)
              <input
                type="file"
                accept=".pdf,.docx,.odt,.rtf,.txt,application/pdf"
                onChange={(event) => void ingestDocument(event)}
                disabled={documentLoading || chatLoading}
              />
            </label>
            {documentName && (
              <p className="muted">
                Загружен: <strong>{documentName}</strong> ({documentText.length.toLocaleString("ru-RU")} симв.){" "}
                <button
                  type="button"
                  className="link-button"
                  onClick={() => {
                    setDocumentName("");
                    setDocumentText("");
                  }}
                >
                  Убрать
                </button>
              </p>
            )}
            {documentText && (
              <details>
                <summary>Текст документа (фрагмент)</summary>
                <pre className="text-preview document-preview">
                  {documentText.slice(0, 3000)}
                  {documentText.length > 3000 ? "\n…" : ""}
                </pre>
              </details>
            )}
            <label>
              Модель Ollama
              <select
                value={selectedModel}
                onChange={(event) => setSelectedModel(event.target.value)}
                disabled={modelsLoading || chatLoading}
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
            {modelsError && <p className="muted">{modelsError}</p>}
            <details className="settings-panel">
              <summary>Промпт для чата</summary>
              <label>
                Инструкция для Ollama
                <textarea value={chatPrompt} onChange={(event) => setChatPrompt(event.target.value)} rows={5} />
              </label>
            </details>
            <div className="chat-thread" aria-live="polite">
              {chatMessages.length === 0 && (
                <p className="muted">Напишите, что нужно уточнить или дополнить в контексте проекта на основе загруженного документа.</p>
              )}
              {chatMessages.map((turn, index) => (
                <article key={`${turn.role}-${index}`} className={`chat-bubble chat-bubble-${turn.role}`}>
                  <strong>{turn.role === "user" ? "Вы" : "ИИ"}</strong>
                  <p>{turn.content}</p>
                </article>
              ))}
            </div>
            <form onSubmit={(event) => void sendChat(event)} className="stack-form chat-compose">
              <label>
                Сообщение
                <textarea
                  value={chatInput}
                  onChange={(event) => setChatInput(event.target.value)}
                  rows={3}
                  placeholder="Например: перенеси из документа наименование объекта и сроки в narratives и assignment"
                  disabled={chatLoading}
                />
              </label>
              <button type="submit" disabled={chatLoading || !chatInput.trim()}>
                {chatLoading ? "ИИ формирует ответ…" : "Отправить"}
              </button>
            </form>
            {changesSummary && (
              <div className="result-block">
                <h4>Изменения в пакете</h4>
                <p>{changesSummary}</p>
              </div>
            )}
            {suggestedPackage && (
              <div className="button-row">
                <button type="button" onClick={() => applySuggestedToEditor()} disabled={loading}>
                  Применить к редактору JSON
                </button>
                <button type="button" onClick={() => void applySuggestedAndSave()} disabled={loading}>
                  Применить и сохранить в базу
                </button>
              </div>
            )}
          </div>
        )}

        <div className="card project-context-package span-wide">
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
