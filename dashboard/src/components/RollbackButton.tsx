"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { rollbackAction } from "@/lib/api";

export function RollbackButton({ actionId }: { actionId: string }) {
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleRollback() {
    setLoading(true);
    await rollbackAction(actionId);
    setLoading(false);
    router.refresh();
  }

  return (
    <button
      type="button"
      onClick={() => void handleRollback()}
      disabled={loading}
      className="text-xs px-2 py-1 rounded border border-guardian-accent/50 text-guardian-accent hover:bg-guardian-accent/10 disabled:opacity-50"
    >
      {loading ? "..." : "Rollback"}
    </button>
  );
}
