"use client";

import { useState } from "react";
import type { Playbook } from "../types";
import { PlaybookCard } from "./PlaybookCard";

export function PlaybooksClient() {
  const [playbooks] = useState<Playbook[]>([]);

  return (
    <div className="px-8 py-7">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Playbooks</h1>
        <p className="mt-1 text-sm text-ink-soft">Orchestrated AI workflows</p>
      </div>

      {playbooks.length > 0 ? (
        <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3">
          {playbooks.map((playbook) => (
            <PlaybookCard key={playbook.id} playbook={playbook} />
          ))}
        </div>
      ) : (
        <div className="mt-16 text-center text-sm text-ink-muted">No playbooks yet.</div>
      )}
    </div>
  );
}
