import { Lock, MessageSquare, Play } from "lucide-react";
import type { Playbook } from "../types";
import { FRAMEWORK_COLORS, STATUS_COLORS } from "../types";

function softStyle(color: string) {
  return { color, backgroundColor: `${color}1a` };
}

export function PlaybookCard({ playbook }: { playbook: Playbook }) {
  const frameworkColor = FRAMEWORK_COLORS[playbook.framework];
  const statusColor = STATUS_COLORS[playbook.status];

  return (
    <div className="flex flex-col rounded-xl border border-line bg-white p-5 transition-shadow duration-200 hover:shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 items-center gap-2">
          <h3 className="truncate text-sm font-semibold text-ink">
            {playbook.name}
          </h3>
          {playbook.locked && (
            <Lock className="h-3.5 w-3.5 flex-shrink-0 text-ink-muted" />
          )}
          <span
            className="h-2 w-2 flex-shrink-0 rounded-full"
            style={{ backgroundColor: statusColor }}
            aria-label={playbook.status}
          />
        </div>
        <span
          className="flex flex-shrink-0 items-center gap-1.5 rounded-md px-2 py-0.5 text-xs font-medium"
          style={softStyle(frameworkColor)}
        >
          <span
            className="h-1.5 w-1.5 rounded-full"
            style={{ backgroundColor: frameworkColor }}
          />
          {playbook.framework}
        </span>
      </div>

      <p className="mt-3 line-clamp-2 min-h-[2.6rem] text-sm leading-relaxed text-ink-soft">
        {playbook.description}
      </p>

      {playbook.tag && (
        <div className="mt-4">
          <span
            className="inline-flex rounded-full px-2.5 py-1 text-xs font-medium"
            style={softStyle(playbook.tag.color)}
          >
            {playbook.tag.label}
          </span>
        </div>
      )}

      <div className="mt-4 flex items-center justify-between text-xs text-ink-muted">
        <div className="flex items-center gap-4">
          <span>{playbook.agents} agents</span>
          <span>{playbook.steps} steps</span>
        </div>
        <span>{playbook.updatedAgo}</span>
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-line pt-4">
        <span className="truncate text-xs text-ink-muted">
          by {playbook.author}
        </span>
        <button
          type="button"
          className="flex flex-shrink-0 items-center gap-1.5 rounded-lg bg-ink px-3 py-1.5 text-xs font-medium text-white transition-opacity duration-200 hover:opacity-90"
        >
          {playbook.action === "run" ? (
            <>
              <Play className="h-3.5 w-3.5" strokeWidth={1.9} />
              Run
            </>
          ) : (
            <>
              <MessageSquare className="h-3.5 w-3.5" strokeWidth={1.9} />
              Chat
            </>
          )}
        </button>
      </div>
    </div>
  );
}
