import { BookOpen } from "lucide-react";

type SummaryRow = { label: string; value: number };

export function SummaryPanel({
  name,
  tagCount,
  agentCount,
  toolCount,
  skillCount,
  knowledgeBaseCount,
}: {
  name: string;
  tagCount: number;
  agentCount: number;
  toolCount: number;
  skillCount: number;
  knowledgeBaseCount: number;
}) {
  const rows: SummaryRow[] = [
    { label: "Agents", value: agentCount },
    { label: "Tools", value: toolCount },
    { label: "Skills", value: skillCount },
    { label: "Knowledge bases", value: knowledgeBaseCount },
    { label: "Steps", value: 0 },
    { label: "Tags", value: tagCount },
  ];

  return (
    <aside className="w-full rounded-xl border border-line bg-white p-5 lg:w-[300px] lg:flex-shrink-0">
      <div className="flex items-center gap-2">
        <BookOpen className="h-4 w-4 text-ink-soft" strokeWidth={1.9} />
        <span className="text-sm font-semibold text-ink">
          {name.trim() || "Unnamed playbook"}
        </span>
      </div>

      <div className="mt-4 flex flex-col gap-3">
        {rows.map((row) => (
          <div
            key={row.label}
            className="flex items-center justify-between text-sm"
          >
            <span className="text-ink-soft">{row.label}</span>
            <span className="font-medium text-ink">{row.value}</span>
          </div>
        ))}
      </div>

      <div className="mt-5 border-t border-line pt-4">
        <p className="text-sm font-medium text-amber-600">Draft</p>
        <p className="mt-1 text-xs text-ink-muted">
          Publish after saving to use in executions.
        </p>
      </div>
    </aside>
  );
}
