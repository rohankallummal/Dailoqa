"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { IdentityTab } from "./IdentityTab";
import { EngineConfigTab } from "./EngineConfigTab";
import type { Engine, PlaybookType } from "./EngineConfigTab";
import { ResourcesTab } from "./ResourcesTab";
import type { SelectedResources } from "./ResourcesTab";
import { AccessTab } from "./AccessTab";
import type { Visibility } from "./AccessTab";
import { SummaryPanel } from "./SummaryPanel";

const emptyResources: SelectedResources = {
  agents: [],
  tools: [],
  skills: [],
  knowledgeBases: [],
};

const TABS = [
  "Identity",
  "Engine & Config",
  "Resources",
  "Workflow",
  "Access",
] as const;

type TabName = (typeof TABS)[number];

export function CreatePlaybookClient() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<TabName>("Identity");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [playbookType, setPlaybookType] = useState<PlaybookType>("one-shot");
  const [engine, setEngine] = useState<Engine>("MAF");
  const [instructions, setInstructions] = useState("");
  const [modelOverride, setModelOverride] = useState(false);
  const [resources, setResources] = useState<SelectedResources>(emptyResources);
  const [visibility, setVisibility] = useState<Visibility>("private");

  return (
    <div className="px-8 py-7">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Create Playbook</h1>
        <p className="mt-1 text-sm text-ink-soft">
          Orchestrate agents into a workflow
        </p>
      </div>

      <div className="mt-6 flex gap-6 border-b border-line">
        {TABS.map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={`-mb-px border-b-2 pb-3 text-sm transition-colors ${
              activeTab === tab
                ? "border-ink font-medium text-ink"
                : "border-transparent text-ink-soft hover:text-ink"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="mt-6 flex flex-col gap-6 lg:flex-row">
        <div className="min-w-0 flex-1">
          {activeTab === "Identity" && (
            <IdentityTab
              name={name}
              onNameChange={setName}
              description={description}
              onDescriptionChange={setDescription}
              tags={tags}
              onTagsChange={setTags}
            />
          )}
          {activeTab === "Engine & Config" && (
            <EngineConfigTab
              playbookType={playbookType}
              onPlaybookTypeChange={setPlaybookType}
              engine={engine}
              onEngineChange={setEngine}
              instructions={instructions}
              onInstructionsChange={setInstructions}
              modelOverride={modelOverride}
              onModelOverrideChange={setModelOverride}
            />
          )}
          {activeTab === "Resources" && (
            <ResourcesTab selected={resources} onChange={setResources} />
          )}
          {activeTab === "Access" && (
            <AccessTab visibility={visibility} onVisibilityChange={setVisibility} />
          )}
          {activeTab === "Workflow" && <PlaceholderTab title={activeTab} />}

          <div className="mt-6 flex justify-end gap-3">
            <button
              type="button"
              onClick={() => router.push("/playbooks")}
              className="rounded-lg border border-line bg-white px-4 py-2.5 text-sm font-medium text-ink-soft transition-colors duration-200 hover:bg-hover"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={() => router.push("/playbooks")}
              className="rounded-lg bg-ink px-5 py-2.5 text-sm font-medium text-white transition-opacity duration-200 hover:opacity-90"
            >
              Create playbook
            </button>
          </div>
        </div>

        <SummaryPanel
          name={name}
          tagCount={tags.length}
          agentCount={resources.agents.length}
          toolCount={resources.tools.length}
          skillCount={resources.skills.length}
          knowledgeBaseCount={resources.knowledgeBases.length}
        />
      </div>
    </div>
  );
}

function PlaceholderTab({ title }: { title: string }) {
  return (
    <div className="flex min-h-[280px] items-center justify-center rounded-xl border border-line bg-white p-6">
      <p className="text-sm text-ink-muted">{title} — coming soon</p>
    </div>
  );
}
