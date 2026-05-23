import type { ActionRecord } from "@/lib/api";
import { RollbackButton } from "./RollbackButton";

interface Props {
  actions: ActionRecord[];
}

function riskColor(score: number): string {
  if (score >= 80) return "text-guardian-danger";
  if (score >= 50) return "text-guardian-warn";
  return "text-guardian-safe";
}

export function ActionFeed({ actions }: Props) {
  if (actions.length === 0) {
    return (
      <p className="text-slate-400 text-sm p-6">
        No actions yet. Run an agent with <code className="text-guardian-accent">@guardian.watch</code>{" "}
        or start the API.
      </p>
    );
  }

  return (
    <ul className="divide-y divide-slate-800">
      {actions.map((a) => (
        <li key={a.action_id} className="p-4 hover:bg-slate-900/50 transition">
          <div className="flex justify-between items-start gap-4">
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-mono text-xs text-guardian-accent">{a.action_id}</span>
                <span
                  className={`text-xs font-semibold uppercase ${riskColor(a.risk_score)}`}
                >
                  {a.risk_score}/100
                </span>
                <span className="text-xs text-slate-500">{a.category}</span>
              </div>
              <p className="font-mono text-sm text-slate-300 truncate">{a.call_repr}</p>
              <p className="text-xs text-slate-500 mt-1">{a.explanation}</p>
            </div>
            <div className="flex flex-col items-end gap-2 shrink-0">
              <span
                className={`text-xs px-2 py-0.5 rounded ${
                  a.status === "blocked"
                    ? "bg-rose-900/50 text-rose-300"
                    : a.status === "executed"
                      ? "bg-emerald-900/50 text-emerald-300"
                      : "bg-slate-800 text-slate-400"
                }`}
              >
                {a.status}
              </span>
              {a.status === "executed" && <RollbackButton actionId={a.action_id} />}
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
}
