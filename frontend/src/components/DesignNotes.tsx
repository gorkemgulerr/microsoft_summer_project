import { designNotes, lessonsLearned } from "../data/content";
import "./DesignNotes.css";

export default function DesignNotes() {
  return (
    <div className="design-notes">
      <dl className="notes-grid">
        {designNotes.map((n) => (
          <div key={n.title} className="notes-row">
            <dt>{n.title}</dt>
            <dd>{n.body}</dd>
          </div>
        ))}
      </dl>

      <h3 className="lessons-heading">Lessons Learned</h3>
      <ol className="lessons-list">
        {lessonsLearned.map((l) => (
          <li key={l.title}>
            <p className="lesson-title">{l.title}</p>
            <p className="lesson-body">{l.body}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}
