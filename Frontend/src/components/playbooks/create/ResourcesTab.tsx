"use client";

import { Bot, Wrench, Lightbulb, BookMarked } from "lucide-react";
import { ResourcePicker } from "./ResourcePicker";
import {
  availableAgents,
  availableTools,
  availableSkills,
  availableKnowledgeBases,
} from "./resourceData";

export type SelectedResources = {
  agents: string[];
  tools: string[];
  skills: string[];
  knowledgeBases: string[];
};

export function ResourcesTab({
  selected,
  onChange,
}: {
  selected: SelectedResources;
  onChange: (next: SelectedResources) => void;
}) {
  return (
    <div className="flex flex-col gap-5">
      <ResourcePicker
        label="AGENTS"
        required
        description="Select the agents that will participate in this playbook."
        icon={Bot}
        buttonLabel="Select agents"
        options={availableAgents}
        selectedIds={selected.agents}
        onChange={(agents) => onChange({ ...selected, agents })}
      />

      <ResourcePicker
        label="TOOLS"
        description="Attach tools the orchestrator or agents can call directly."
        icon={Wrench}
        buttonLabel="Select tools"
        options={availableTools}
        selectedIds={selected.tools}
        onChange={(tools) => onChange({ ...selected, tools })}
      />

      <ResourcePicker
        label="SKILLS"
        description="Attach published skills to inject at execution time."
        icon={Lightbulb}
        buttonLabel="Select skills"
        options={availableSkills}
        selectedIds={selected.skills}
        onChange={(skills) => onChange({ ...selected, skills })}
      />

      <ResourcePicker
        label="KNOWLEDGE BASES"
        description="Attach published knowledge bases for retrieval."
        icon={BookMarked}
        buttonLabel="Select knowledge bases"
        options={availableKnowledgeBases}
        selectedIds={selected.knowledgeBases}
        onChange={(knowledgeBases) => onChange({ ...selected, knowledgeBases })}
      />
    </div>
  );
}
