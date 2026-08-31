import { architectureSteps } from "../data/content";
import "./ArchitectureDiagram.css";

const STEP_W = 176;
const STEP_H = 92;
const GAP = 46;
const TOP = 16;
const START_X = 16;

export default function ArchitectureDiagram() {
  const width = START_X * 2 + architectureSteps.length * STEP_W + (architectureSteps.length - 1) * GAP;
  const height = TOP * 2 + STEP_H + 34;

  return (
    <div className="arch-diagram-wrap">
      <svg
        className="arch-diagram"
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label="Pipeline: Ingest, then Embed, then Store, then Retrieve, then Generate"
      >
        {architectureSteps.map((step, i) => {
          const x = START_X + i * (STEP_W + GAP);
          const y = TOP;
          const cx = x + STEP_W / 2;
          const cy = y + STEP_H / 2;
          return (
            <g key={step.label}>
              <rect
                x={x}
                y={y}
                width={STEP_W}
                height={STEP_H}
                rx={4}
                className="arch-box"
              />
              <text x={cx} y={cy - 12} textAnchor="middle" className="arch-step-label">
                {step.label}
              </text>
              <foreignObject x={x + 10} y={cy - 2} width={STEP_W - 20} height={44}>
                <div className={step.mono ? "arch-detail mono" : "arch-detail"}>{step.detail}</div>
              </foreignObject>
              <text x={cx} y={y - 4} textAnchor="middle" className="arch-index">
                {String(i + 1).padStart(2, "0")}
              </text>

              {i < architectureSteps.length - 1 && (
                <g className="arch-arrow">
                  <line x1={x + STEP_W} y1={cy} x2={x + STEP_W + GAP - 10} y2={cy} />
                  <polygon
                    points={`
                      ${x + STEP_W + GAP - 10},${cy - 5}
                      ${x + STEP_W + GAP},${cy}
                      ${x + STEP_W + GAP - 10},${cy + 5}
                    `}
                  />
                </g>
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
