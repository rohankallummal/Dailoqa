type DocsNavItem = {
  label: string;
  href: string;
};

export const docsNavItems: DocsNavItem[] = [
  { label: "Overview", href: "/docs" },
  { label: "DeepAgents", href: "/docs/deepagents" },
  { label: "LangChain", href: "/docs/langchain" },
  { label: "LangGraph", href: "/docs/langgraph" },
];

export type DocsSideNavItem = {
  label: string;
  href: string;
  source: string;
};

type DocsSideNavSection = {
  primary: DocsSideNavItem[];
  pages: DocsSideNavItem[];
};

export const docsSideNav: Record<string, DocsSideNavSection> = {
  langchain: {
    primary: [
      {
        label: "Overview",
        href: "/docs/langchain",
        source: "/oss/langchain/overview",
      },
    ],
    pages: [
      {
        label: "Prebuilt Middleware",
        href: "/docs/langchain/prebuilt-middleware",
        source: "/oss/langchain/middleware/built-in",
      },
      {
        label: "Agents",
        href: "/docs/langchain/agents",
        source: "/oss/langchain/agents",
      },
      {
        label: "Models",
        href: "/docs/langchain/models",
        source: "/oss/langchain/models",
      },
      {
        label: "Guardrails",
        href: "/docs/langchain/guardrails",
        source: "/oss/langchain/guardrails",
      },
      {
        label: "Structured Output",
        href: "/docs/langchain/structured-output",
        source: "/oss/langchain/structured-output",
      },
    ],
  },
  langgraph: {
    primary: [
      {
        label: "Overview",
        href: "/docs/langgraph",
        source: "/oss/langgraph/overview",
      },
    ],
    pages: [
      {
        label: "Persistence",
        href: "/docs/langgraph/persistence",
        source: "/oss/langgraph/persistence",
      },
      {
        label: "Checkpoints",
        href: "/docs/langgraph/checkpoints",
        source: "/oss/langgraph/checkpointers",
      },
      {
        label: "Stores",
        href: "/docs/langgraph/stores",
        source: "/oss/langgraph/stores",
      },
      {
        label: "Interrupts",
        href: "/docs/langgraph/interrupts",
        source: "/oss/langgraph/interrupts",
      },
      {
        label: "Subgraphs",
        href: "/docs/langgraph/subgraphs",
        source: "/oss/langgraph/use-subgraphs",
      },
    ],
  },
  deepagents: {
    primary: [
      {
        label: "Overview",
        href: "/docs/deepagents",
        source: "/oss/deepagents/overview",
      },
    ],
    pages: [
      {
        label: "Subagents",
        href: "/docs/deepagents/subagents",
        source: "/oss/deepagents/subagents",
      },
      {
        label: "Skills",
        href: "/docs/deepagents/skills",
        source: "/oss/deepagents/skills",
      },
      {
        label: "Sandboxes",
        href: "/docs/deepagents/sandboxes",
        source: "/oss/deepagents/sandboxes",
      },
      {
        label: "Multimodality",
        href: "/docs/deepagents/multimodality",
        source: "/oss/deepagents/multimodal",
      },
      {
        label: "Tools",
        href: "/docs/deepagents/tools",
        source: "/oss/deepagents/tools",
      },
    ],
  },
};

export const docsPages: DocsSideNavItem[] = Object.values(docsSideNav).flatMap((section) => [
  ...section.primary,
  ...section.pages,
]);

export const docsSourceHrefs: Record<string, string> = Object.fromEntries(
  docsPages.map((item) => [item.source, item.href]),
);

export const docsPageSources: Record<string, string> = Object.fromEntries(
  docsPages.map((item) => [item.href, `${item.source.replace("/oss/", "")}.mdx`]),
);
