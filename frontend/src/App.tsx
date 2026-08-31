import { useEffect, useState } from "react";
import "./App.css";
import ArchitectureDiagram from "./components/ArchitectureDiagram";
import QAPanel from "./components/QAPanel";
import TestResults from "./components/TestResults";
import PerformancePanel from "./components/PerformancePanel";
import DesignNotes from "./components/DesignNotes";
import { keyFeatures } from "./data/content";

type Theme = "light" | "dark";

function getInitialTheme(): Theme {
  const stored = localStorage.getItem("theme");
  if (stored === "light" || stored === "dark") return stored;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function App() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <div className="page">
      <header className="page-header">
        <div className="page-header-top">
          <p className="eyebrow">Microsoft Summer School &middot; Foundry Local</p>
          <button
            type="button"
            className="theme-toggle"
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
            aria-label="Toggle color theme"
          >
            {theme === "light" ? "Dark" : "Light"} mode
          </button>
        </div>
        <h1>Foundry Local RAG Assistant</h1>
        <p className="lede">
          A local Retrieval-Augmented Generation question-answering assistant. Answers are
          grounded in a private knowledge base and generated entirely on-device — no cloud
          calls, no API keys, no data leaving the machine.
        </p>
        <ul className="feature-list">
          {keyFeatures.map((f) => (
            <li key={f.feature}>
              <span className="feature-name">{f.feature}</span>
              <span className="feature-detail">{f.detail}</span>
            </li>
          ))}
        </ul>
      </header>

      <main>
        <section className="section" id="architecture">
          <h2>Architecture</h2>
          <p className="section-intro">
            Documents are chunked, embedded, and stored once at ingestion time. Each query
            re-embeds only the question, ranks stored chunks by cosine similarity, and passes
            the top matches to the chat model as grounding context.
          </p>
          <ArchitectureDiagram />
        </section>

        <section className="section" id="ask">
          <h2>Ask the Assistant</h2>
          <p className="section-intro">
            Connects to the FastAPI backend at <code>POST /ask</code>, which wraps the
            existing <code>rag.answer_query()</code> pipeline.
          </p>
          <QAPanel />
        </section>

        <section className="section" id="results">
          <h2>Test Results</h2>
          <TestResults />
        </section>

        <section className="section" id="performance">
          <h2>Performance</h2>
          <PerformancePanel />
        </section>

        <section className="section" id="design">
          <h2>Design Decisions &amp; Limitations</h2>
          <DesignNotes />
        </section>
      </main>

      <footer className="page-footer">
        <p>
          Foundry Local RAG Assistant &mdash; built for the Microsoft Summer School, Demo Day
          2026. Source, presentation, and full test log in the project repository.
        </p>
      </footer>
    </div>
  );
}

export default App;
