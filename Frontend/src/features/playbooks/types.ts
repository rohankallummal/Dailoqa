export type Framework = "LangGraph" | "MAF";

export type PlaybookStatus = "active" | "draft";

export type PlaybookAction = "chat" | "run";

export type PlaybookTag = {
  label: string;
  color: string;
};

export type Playbook = {
  id: string;
  name: string;
  description: string;
  framework: Framework;
  status: PlaybookStatus;
  locked: boolean;
  tag?: PlaybookTag;
  agents: number;
  steps: number;
  updatedAgo: string;
  author: string;
  action: PlaybookAction;
};

export const FRAMEWORK_COLORS: Record<Framework, string> = {
  LangGraph: "#6c5cf5",
  MAF: "#0ea5e9",
};

export const STATUS_COLORS: Record<PlaybookStatus, string> = {
  active: "#22c55e",
  draft: "#f59e0b",
};
