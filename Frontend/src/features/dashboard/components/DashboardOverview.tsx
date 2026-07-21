import {
  Activity,
  CircleCheck,
  Clock,
  BookOpen,
  Play,
  Wrench,
  Bot,
} from "lucide-react";

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
        <div
          className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-active text-4xl"
          aria-hidden="true"
        >
          🧑‍🔬
        </div>
      </header>

      <section
        className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4"
        aria-label="Overview"
      >
        <article className="rounded-2xl border border-line bg-white p-6 shadow-sm">
          <div className="flex items-start justify-between gap-3">
            <span className="max-w-[150px] text-xs font-medium uppercase leading-snug tracking-wider text-ink-soft">
              Active executions
            </span>
            <span
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-hover text-ink-soft"
              aria-hidden="true"
            >
              <Activity className="h-5 w-5" />
            </span>
          </div>
          <p className="mt-4 text-4xl font-bold tracking-tight text-ink">0</p>
          <p className="mt-2 text-sm text-ink-muted">No active executions</p>
        </article>

        <article className="rounded-2xl border border-line bg-white p-6 shadow-sm">
          <div className="flex items-start justify-between gap-3">
            <span className="max-w-[150px] text-xs font-medium uppercase leading-snug tracking-wider text-ink-soft">
              Completed today
            </span>
            <span
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-hover text-ink-soft"
              aria-hidden="true"
            >
              <CircleCheck className="h-5 w-5" />
            </span>
          </div>
          <p className="mt-4 text-4xl font-bold tracking-tight text-ink">0</p>
          <p className="mt-2 text-sm text-ink-muted">&nbsp;</p>
        </article>

        <article className="rounded-2xl border border-line bg-white p-6 shadow-sm">
          <div className="flex items-start justify-between gap-3">
            <span className="max-w-[150px] text-xs font-medium uppercase leading-snug tracking-wider text-ink-soft">
              Pending approvals
            </span>
            <span
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-hover text-ink-soft"
              aria-hidden="true"
            >
              <Clock className="h-5 w-5" />
            </span>
          </div>
          <p className="mt-4 text-4xl font-bold tracking-tight text-ink">0</p>
          <p className="mt-2 text-sm text-ink-muted">All clear</p>
        </article>

        <article className="rounded-2xl border border-line bg-white p-6 shadow-sm">
          <div className="flex items-start justify-between gap-3">
            <span className="max-w-[150px] text-xs font-medium uppercase leading-snug tracking-wider text-ink-soft">
              Published playbooks
            </span>
            <span
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-hover text-ink-soft"
              aria-hidden="true"
            >
              <BookOpen className="h-5 w-5" />
            </span>
          </div>
          <p className="mt-4 text-4xl font-bold tracking-tight text-ink">0</p>
          <p className="mt-2 text-sm text-ink-muted">0 ready to run</p>
        </article>
      </section>

      <h2 className="mb-4 mt-10 text-base font-semibold text-ink">
        Quick Actions
      </h2>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <button className="flex items-start gap-5 rounded-2xl border border-line bg-white p-6 text-left shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-accent/40 hover:shadow-md">
          <span
            className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-active text-accent"
            aria-hidden="true"
          >
            <Play className="h-6 w-6" />
          </span>
          <span>
            <h3 className="text-base font-semibold text-ink">Run a Playbook</h3>
            <p className="mt-1.5 text-sm leading-relaxed text-ink-muted">
              Execute an agent workflow against your data
            </p>
          </span>
        </button>

        <button className="flex items-start gap-5 rounded-2xl border border-line bg-white p-6 text-left shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-accent/40 hover:shadow-md">
          <span
            className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-active text-accent"
            aria-hidden="true"
          >
            <Wrench className="h-6 w-6" />
          </span>
          <span>
            <h3 className="text-base font-semibold text-ink">Create a Tool</h3>
            <p className="mt-1.5 text-sm leading-relaxed text-ink-muted">
              Connect an external API or MCP server
            </p>
          </span>
        </button>

        <button className="flex items-start gap-5 rounded-2xl border border-line bg-white p-6 text-left shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-accent/40 hover:shadow-md">
          <span
            className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-active text-accent"
            aria-hidden="true"
          >
            <Bot className="h-6 w-6" />
          </span>
          <span>
            <h3 className="text-base font-semibold text-ink">Build an Agent</h3>
            <p className="mt-1.5 text-sm leading-relaxed text-ink-muted">
              Configure an AI agent with tools and instructions
            </p>
          </span>
        </button>
      </div>
    </div>
  );
}
