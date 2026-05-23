const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface ActionRecord {
  action_id: string;
  call_repr: string;
  risk_score: number;
  category: string;
  status: string;
  timestamp: string;
  explanation: string;
}

export interface Stats {
  total: number;
  blocked: number;
  executed: number;
  avg_risk: number;
}

export async function fetchActions(): Promise<ActionRecord[]> {
  const res = await fetch(`${API_URL}/actions`, { cache: "no-store" });
  if (!res.ok) return [];
  return res.json() as Promise<ActionRecord[]>;
}

export async function fetchStats(): Promise<Stats> {
  const res = await fetch(`${API_URL}/actions/stats`, { cache: "no-store" });
  if (!res.ok) return { total: 0, blocked: 0, executed: 0, avg_risk: 0 };
  return res.json() as Promise<Stats>;
}

export async function rollbackAction(actionId: string): Promise<boolean> {
  const res = await fetch(`${API_URL}/rollback/${actionId}`, { method: "POST" });
  if (!res.ok) return false;
  const data = (await res.json()) as { success: boolean };
  return data.success;
}
