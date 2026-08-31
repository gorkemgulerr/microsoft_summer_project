import { testSummary } from "../data/content";
import "./TestResults.css";

export default function TestResults() {
  const totalPassed = testSummary.categories.reduce((s, c) => s + c.passed, 0);
  const totalCount = testSummary.categories.reduce((s, c) => s + c.total, 0);

  return (
    <div className="results">
      <div className="results-headline">
        <span className="results-score">
          {totalPassed}/{totalCount}
        </span>
        <div className="results-headline-text">
          <p>functional tests passed</p>
          <p className="results-meta mono">
            {testSummary.date} &middot; {testSummary.chunkCount} chunks &middot;{" "}
            {testSummary.documentCount} documents
          </p>
        </div>
      </div>

      <table className="results-table">
        <thead>
          <tr>
            <th>Category</th>
            <th>Passed</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          {testSummary.categories.map((c) => (
            <tr key={c.category}>
              <td>{c.category}</td>
              <td className="mono">{c.passed}</td>
              <td className="mono">{c.total}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="results-columns">
        <div>
          <h3>Answerable</h3>
          <ol className="results-list">
            {testSummary.answerable.map((q) => (
              <li key={q}>
                <span className="pass-badge good">PASS</span>
                {q}
              </li>
            ))}
          </ol>
        </div>
        <div>
          <h3>Unanswerable (correct fallback)</h3>
          <ol className="results-list">
            {testSummary.unanswerable.map((q) => (
              <li key={q}>
                <span className="pass-badge good">PASS</span>
                {q}
              </li>
            ))}
          </ol>
          <h3 className="edge-heading">Edge cases</h3>
          <ul className="results-list edge-list">
            {testSummary.edgeCases.map((e) => (
              <li key={e.label}>
                <span className="pass-badge good">PASS</span>
                <span>
                  <strong>{e.label}</strong> ({e.input}) &mdash; {e.result}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
