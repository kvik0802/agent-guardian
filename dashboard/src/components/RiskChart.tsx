import type { Stats } from "@/lib/api";

interface Props {
  stats: Stats;
}

export function RiskChart({ stats }: Props) {
  const max = Math.max(stats.total, 1);
  const bars = [
    { label: "Total", value: stats.total, color: "bg-guardian-accent" },
    { label: "Blocked", value: stats.blocked, color: "bg-guardian-danger" },
    { label: "Executed", value: stats.executed, color: "bg-guardian-safe" },
  ];

  return (
    <div className="p-6">
      <h2 className="text-sm font-medium text-slate-400 mb-4">Risk overview</h2>
      <p className="text-3xl font-bold text-white mb-6">
        {stats.avg_risk}
        <span className="text-lg text-slate-500 font-normal"> avg risk</span>
      </p>
      <div className="space-y-3">
        {bars.map((b) => (
          <div key={b.label}>
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>{b.label}</span>
              <span>{b.value}</span>
            </div>
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className={`h-full ${b.color} rounded-full transition-all`}
                style={{ width: `${(b.value / max) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
