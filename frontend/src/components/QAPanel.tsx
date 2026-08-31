import { useEffect, useState, type FormEvent } from "react";
import { askQuestion, getHealth, type AskResponse } from "../api";
import { sampleQA } from "../data/content";
import "./QAPanel.css";

type HealthState =
  | { state: "checking" }
  | { state: "ok"; chunkCount: number }
  | { state: "empty" }
  | { state: "unreachable" };

export default function QAPanel() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<HealthState>({ state: "checking" });

  useEffect(() => {
    let cancelled = false;
    getHealth()
      .then((h) => {
        if (cancelled) return;
        setHealth(h.status === "ok" ? { state: "ok", chunkCount: h.chunk_count } : { state: "empty" });
      })
      .catch(() => {
        if (!cancelled) setHealth({ state: "unreachable" });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!question.trim() || loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await askQuestion(question.trim());
      setResult(res);
    } catch {
      setError(
        "Could not reach the backend. Make sure the FastAPI server is running: uvicorn api:app --reload --port 8000"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="qa-panel">
      <div className={`health-strip health-${health.state}`}>
        {health.state === "checking" && "Checking backend status…"}
        {health.state === "ok" && `Backend connected — knowledge base loaded, ${health.chunkCount} chunks indexed.`}
        {health.state === "empty" && "Backend connected, but the knowledge base is empty. Run python ingest.py."}
        {health.state === "unreachable" &&
          "Backend unreachable at " +
            (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000") +
            ". Start it with: uvicorn api:app --reload --port 8000"}
      </div>

      <form className="qa-form" onSubmit={handleSubmit}>
        <label htmlFor="question" className="qa-label">
          Question
        </label>
        <textarea
          id="question"
          className="qa-input"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. What is RAG and what problem does it solve?"
          rows={2}
        />
        <button type="submit" className="qa-submit" disabled={loading || !question.trim()}>
          {loading ? "Retrieving …" : "Ask"}
        </button>
      </form>

      <div className="qa-examples">
        <span className="qa-examples-label">Try:</span>
        {sampleQA.map((s) => (
          <button
            type="button"
            key={s.question}
            className="qa-example-chip"
            onClick={() => setQuestion(s.question)}
          >
            {s.question}
          </button>
        ))}
      </div>

      {error && <div className="qa-error">{error}</div>}

      {result && (
        <div className="qa-result">
          <p className="qa-answer">{result.answer}</p>
          <div className="qa-meta">
            <div className="qa-sources">
              <span className="qa-meta-label">Sources</span>
              {result.sources.length === 0 ? (
                <span className="qa-source-chip qa-source-none">none above threshold</span>
              ) : (
                result.sources.map((s) => (
                  <span key={s} className="qa-source-chip mono">
                    {s}
                  </span>
                ))
              )}
            </div>
            <div className="qa-elapsed">
              <span className="qa-meta-label">Elapsed</span>
              <span className="mono">{result.elapsed_s.toFixed(2)}s</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
