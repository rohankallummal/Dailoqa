export type NavItem = {
  label: string;
  href: string;
  icon: string;
  newTab?: boolean;
};

export type NavSection = {
  label?: string;
  items: NavItem[];
};

export const navSections: NavSection[] = [
  {
    items: [
      { label: "Dashboard", href: "/dashboard", icon: "dashboard" },
      { label: "Playbooks", href: "/playbooks", icon: "playbooks" },
      { label: "Executions", href: "/executions", icon: "executions" },
      { label: "Approvals", href: "/approvals", icon: "approvals" },
      { label: "Docs", href: "/docs", icon: "docs", newTab: true },
    ],
  },
  {
    label: "Builder",
    items: [
      { label: "Agents", href: "/agents", icon: "agents" },
      { label: "Tools", href: "/tools", icon: "tools" },
      { label: "Skills", href: "/skills", icon: "skills" },
      { label: "Knowledge Bases", href: "/knowledge-bases", icon: "knowledgeBases" },
      { label: "MCP Servers", href: "/mcp-servers", icon: "mcpServers" },
    ],
  },
];
