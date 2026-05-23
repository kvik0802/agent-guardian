import { ActionFeed } from "@/components/ActionFeed";
import { RiskChart } from "@/components/RiskChart";
import { fetchActions, fetchStats } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [actions, stats] = await Promise.all([fetchActions(), fetchStats()]);

  return (
    <main className="min-h-screen">
      <header className="border-b border-slate-800 px-6 py-8">
        <div className="max-w-6xl mx-auto">
          <p className="text-guardian-accent text-sm font-medium mb-2">Outskill × OpenAI Hackathon</p>
          <h1 className="text-3xl font-bold tracking-tight">
            Agent Guardian
            <span className="text-slate-500 font-normal text-lg ml-3">Live Monitor</span>
          </h1>
          <p className="text-slate-400 mt-2 max-w-2xl">
            Intercept · Detect · Simulate · Approve · Rollback — the safety layer every AI agent needs.
          </p>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-8 grid lg:grid-cols-3 gap-6">
        <section className="lg:col-span-2 bg-guardian-card rounded-xl border border-slate-800 overflow-hidden">
          <h2 className="text-sm font-medium text-slate-400 px-4 py-3 border-b border-slate-800">
            Action feed
          </h2>
          <ActionFeed actions={actions} />
        </section>
        <section className="bg-guardian-card rounded-xl border border-slate-800">
          <RiskChart stats={stats} />
        </section>
      </div>

      <footer className="text-center text-xs text-slate-600 py-8">
        pip install agent-guardian · Built with OpenAI gpt-4o-mini + gpt-4o
      </footer>
    </main>
  );
}
