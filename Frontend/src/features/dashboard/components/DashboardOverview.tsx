import {
  Activity,
  CircleCheck,
  Clock,
  BookOpen,
  Play,
  Wrench,
  Bot,
  type LucideIcon,
} from "lucide-react";

const stats: { label: string; icon: LucideIcon; value: string; caption: string }[] = [
  { label: "Active executions", icon: Activity, value: "0", caption: "No active executions" },
  { label: "Completed today", icon: CircleCheck, value: "0", caption: "\u00a0" },
  { label: "Pending approvals", icon: Clock, value: "0", caption: "All clear" },
  { label: "Published playbooks", icon: BookOpen, value: "0", caption: "0 ready to run" },
];

const quickActions: { title: string; description: string; icon: LucideIcon }[] = [
  {
    title: "Run a Playbook",
    description: "Execute an agent workflow against your data",
    icon: Play,
  },
  {
    title: "Create a Tool",
    description: "Connect an external API or MCP server",
    icon: Wrench,
  },
  {
    title: "Build an Agent",
    description: "Configure an AI agent with tools and instructions",
    icon: Bot,
  },
];

export function DashboardOverview() {
  return (
    <div className="mx-auto max-w-6xl px-8 py-10">
      <header className="flex items-center justify-between gap-8 rounded-2xl border border-line bg-white p-8 shadow-sm">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.14em] text-ink-muted">
            Dashboard
          </p>
          <h1 className="mt-3 text-3xl font-bold tracking-tight text-ink">
            Good afternoon, Dev
          </h1>
          <p className="mt-2.5 text-base text-ink-soft">
            Here&apos;s what&apos;s happening across your AI agents today.
          </p>
        </div>
      </header>

      <section
        className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4"
        aria-label="Overview"
      >
        {stats.map((stat) => (
          <article
            key={stat.label}
            className="rounded-2xl border border-line bg-white p-6 shadow-sm"
          >
            <div className="flex items-start justify-between gap-3">
              <span className="max-w-[150px] text-xs font-medium uppercase leading-snug tracking-wider text-ink-soft">
                {stat.label}
              </span>
              <span
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-hover text-ink-soft"
                aria-hidden="true"
              >
                <stat.icon className="h-5 w-5" />
              </span>
            </div>
            <p className="mt-4 text-4xl font-bold tracking-tight text-ink">{stat.value}</p>
            <p className="mt-2 text-sm text-ink-muted">{stat.caption}</p>
          </article>
        ))}
      </section>

      <h2 className="mb-4 mt-10 text-base font-semibold text-ink">
        Quick Actions
      </h2>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {quickActions.map((action) => (
          <button
            key={action.title}
            className="flex items-start gap-5 rounded-2xl border border-line bg-white p-6 text-left shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-accent/40 hover:shadow-md"
          >
            <span
              className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-active text-accent"
              aria-hidden="true"
            >
              <action.icon className="h-6 w-6" />
            </span>
            <span>
              <h3 className="text-base font-semibold text-ink">{action.title}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-ink-muted">
                {action.description}
              </p>
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
