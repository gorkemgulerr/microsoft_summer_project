import { performanceData } from "../data/content";
import "./PerformancePanel.css";

const CHART_W = 640;
const CHART_H = 220;
const PAD_L = 34;
const PAD_R = 12;
const PAD_T = 16;
const PAD_B = 40;
const BAR_GAP = 18;

function abbreviate(q: string): string {
  const clean = q.replace(" (unanswerable)", "");
  const words = clean.replace("?", "").split(" ");
  return words.slice(0, 3).join(" ") + "…";
}

export default function PerformancePanel() {
  const maxVal = Math.max(...performanceData.raw.map((r) => r.elapsed));
  const scaleMax = Math.ceil(maxVal / 5) * 5;
  const plotW = CHART_W - PAD_L - PAD_R;
  const plotH = CHART_H - PAD_T - PAD_B;
  const barW = (plotW - BAR_GAP * (performanceData.raw.length - 1)) / performanceData.raw.length;

  const y = (v: number) => PAD_T + plotH - (v / scaleMax) * plotH;
  const avgY = y(performanceData.warmAvg);

  const gridTicks = [0, 5, 10, 15, 20, 25, 30].filter((t) => t <= scaleMax);

  return (
    <div className="perf-panel">
      <div className="perf-stats">
        <div className="stat">
          <span className="stat-value mono">{performanceData.warmAvg.toFixed(2)}s</span>
          <span className="stat-label">avg warm-query response</span>
        </div>
        <div className="stat">
          <span className="stat-value mono">{performanceData.coldStart.toFixed(2)}s</span>
          <span className="stat-label">cold start (model load)</span>
        </div>
        <div className="stat">
          <span className="stat-value mono">
            {performanceData.warmRange[0].toFixed(2)}&ndash;{performanceData.warmRange[1].toFixed(2)}s
          </span>
          <span className="stat-label">warm-query range</span>
        </div>
      </div>

      <div className="perf-chart-wrap">
        <svg
          className="perf-chart"
          viewBox={`0 0 ${CHART_W} ${CHART_H}`}
          role="img"
          aria-label="Bar chart of response time in seconds for six benchmark queries"
        >
          {gridTicks.map((t) => (
            <g key={t}>
              <line x1={PAD_L} x2={CHART_W - PAD_R} y1={y(t)} y2={y(t)} className="perf-grid" />
              <text x={PAD_L - 8} y={y(t) + 3} textAnchor="end" className="perf-axis-label mono">
                {t}
              </text>
            </g>
          ))}

          <line
            x1={PAD_L}
            x2={CHART_W - PAD_R}
            y1={avgY}
            y2={avgY}
            className="perf-avg-line"
          />
          <text x={CHART_W - PAD_R} y={avgY - 5} textAnchor="end" className="perf-avg-label mono">
            avg warm {performanceData.warmAvg.toFixed(2)}s
          </text>

          {performanceData.raw.map((r, i) => {
            const x = PAD_L + i * (barW + BAR_GAP);
            const barTop = y(r.elapsed);
            const barH = PAD_T + plotH - barTop;
            return (
              <g key={r.question}>
                <rect
                  x={x}
                  y={barTop}
                  width={barW}
                  height={Math.max(barH, 2)}
                  rx={4}
                  className={r.cold ? "perf-bar perf-bar-cold" : "perf-bar"}
                >
                  <title>{`${r.question} — ${r.elapsed.toFixed(2)}s (${r.chunks} chunks)`}</title>
                </rect>
                <text x={x + barW / 2} y={barTop - 6} textAnchor="middle" className="perf-bar-value mono">
                  {r.elapsed.toFixed(1)}
                </text>
                <text
                  x={x + barW / 2}
                  y={CHART_H - PAD_B + 16}
                  textAnchor="middle"
                  className="perf-x-label"
                >
                  {abbreviate(r.question)}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
      <p className="perf-footnote">
        Measured with <code>time.perf_counter()</code> around the full{" "}
        <code>answer_query()</code> call on Apple Silicon (CPU inference). The first bar
        includes model warm-up (both models loading into memory); it is excluded from the
        warm-query average.
      </p>
    </div>
  );
}
