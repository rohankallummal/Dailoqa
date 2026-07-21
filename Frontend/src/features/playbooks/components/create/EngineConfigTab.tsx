"use client";

import { useState } from "react";
import { Check, ChevronDown } from "lucide-react";

export type PlaybookType = "one-shot" | "chat";
export type Engine = "LangGraph" | "MAF";

const ENGINE_OPTIONS: { label: Engine; id: string }[] = [
  { label: "LangGraph", id: "langgraph" },
  { label: "MAF", id: "maf" },
];

const ORCHESTRATOR_PLACEHOLDER = `Example (Gold Loan Onboarding):
1. Collect the customer's mobile number.
2. Send OTP and validate it (self — use your own tools).
3. Check ETB/NTB status and fetch CIF if ETB.
4. Delegate Aadhaar + PAN validation to the KYC Agent.
5. Delegate CIBIL, AML, and delinquency checks to the Compliance Agent.
6. Delegate property valuation and loan summary to the Valuation Agent.
7. Call complete() with a summary once all stages are done.`;

function Section({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-line bg-white p-6">
      <p className="text-xs font-semibold tracking-wide text-ink-muted">
        {label}
      </p>
      <div className="mt-4">{children}</div>
    </div>
  );
}

export function EngineConfigTab({
  playbookType,
  onPlaybookTypeChange,
  engine,
  onEngineChange,
  instructions,
  onInstructionsChange,
  modelOverride,
  onModelOverrideChange,
}: {
  playbookType: PlaybookType;
  onPlaybookTypeChange: (value: PlaybookType) => void;
  engine: Engine;
  onEngineChange: (value: Engine) => void;
  instructions: string;
  onInstructionsChange: (value: string) => void;
  modelOverride: boolean;
  onModelOverrideChange: (value: boolean) => void;
}) {
  const [engineOpen, setEngineOpen] = useState(false);
  const engineId = ENGINE_OPTIONS.find((o) => o.label === engine)?.id ?? "";

  return (
    <div className="flex flex-col gap-5">
      <Section label="PLAYBOOK TYPE">
        <div className="grid grid-cols-2 gap-3">
          <TypeCard
            title="One-Shot"
            subtitle="Single execution run"
            selected={playbookType === "one-shot"}
            onClick={() => onPlaybookTypeChange("one-shot")}
          />
          <TypeCard
            title="Chat (Interactive)"
            subtitle="Interactive conversation"
            selected={playbookType === "chat"}
            onClick={() => onPlaybookTypeChange("chat")}
          />
        </div>
      </Section>

      <Section label="ENGINE">
        <div className="relative">
          <button
            type="button"
            onClick={() => setEngineOpen((open) => !open)}
            className="flex w-full items-center justify-between rounded-lg border border-line bg-page px-3 py-2.5 text-sm outline-none transition-colors focus:border-accent"
          >
            <span className="flex items-baseline gap-2">
              <span className="font-semibold text-ink">{engine}</span>
              <span className="font-mono text-xs text-ink-muted">
                {engineId}
              </span>
            </span>
            <ChevronDown className="h-4 w-4 text-ink-muted" />
          </button>

          {engineOpen && (
            <>
              <button
                type="button"
                aria-hidden
                tabIndex={-1}
                onClick={() => setEngineOpen(false)}
                className="fixed inset-0 z-10 cursor-default"
              />
              <div className="absolute left-0 right-0 top-full z-20 mt-1 overflow-hidden rounded-lg border border-line bg-white shadow-lg">
                {ENGINE_OPTIONS.map((option) => (
                  <button
                    key={option.id}
                    type="button"
                    onClick={() => {
                      onEngineChange(option.label);
                      setEngineOpen(false);
                    }}
                    className="flex w-full items-center justify-between px-3 py-2.5 text-sm transition-colors hover:bg-hover"
                  >
                    <span className="flex items-baseline gap-2">
                      <span className="font-medium text-ink">
                        {option.label}
                      </span>
                      <span className="font-mono text-xs text-ink-muted">
                        {option.id}
                      </span>
                    </span>
                    {option.label === engine && (
                      <Check className="h-4 w-4 text-accent" />
                    )}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
        <p className="mt-2 text-xs text-ink-soft">
          Engine resolution happens at execution time — changing this affects
          future runs only.
        </p>
      </Section>

      <Section label="ORCHESTRATOR INSTRUCTIONS">
        <p className="text-sm text-ink-soft">
          Describe the full workflow sequence the orchestrator must follow —
          which agents to call, in what order, and when the workflow is
          complete. Individual agent prompts should describe what the agent
          does, not the pipeline order.
        </p>
        <textarea
          value={instructions}
          onChange={(event) => onInstructionsChange(event.target.value)}
          rows={9}
          placeholder={ORCHESTRATOR_PLACEHOLDER}
          className="mt-4 w-full resize-y rounded-lg border border-line bg-white px-3 py-2.5 font-mono text-xs leading-relaxed text-ink outline-none transition-colors focus:border-accent placeholder:text-ink-muted"
        />
      </Section>

      <Section label="MODEL OVERRIDE">
        <div className="-mt-2 flex items-center justify-between">
          <p className="text-sm text-ink-soft">
            Use a specific model instead of the engine default.
          </p>
          <Toggle
            checked={modelOverride}
            onChange={() => onModelOverrideChange(!modelOverride)}
          />
        </div>
      </Section>
    </div>
  );
}

function TypeCard({
  title,
  subtitle,
  selected,
  onClick,
}: {
  title: string;
  subtitle: string;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-lg border bg-white p-4 text-left transition-colors ${
        selected
          ? "border-ink ring-1 ring-ink"
          : "border-line hover:border-ink-muted"
      }`}
    >
      <p className="text-sm font-semibold text-ink">{title}</p>
      <p className="mt-1 text-xs text-ink-soft">{subtitle}</p>
    </button>
  );
}

function Toggle({
  checked,
  onChange,
}: {
  checked: boolean;
  onChange: () => void;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={onChange}
      className={`relative h-6 w-11 flex-shrink-0 rounded-full transition-colors duration-200 ${
        checked ? "bg-accent" : "bg-scrollbar"
      }`}
    >
      <span
        className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform duration-200 ${
          checked ? "translate-x-[22px]" : "translate-x-0.5"
        }`}
      />
    </button>
  );
}
