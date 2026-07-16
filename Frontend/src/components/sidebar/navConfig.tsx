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
  {
    label: "Agentic Data Intelligence",
    items: [
      { label: "Database Management", href: "/database-management", icon: "databaseManagement" },
      { label: "Query on Database", href: "/query-on-database", icon: "queryOnDatabase" },
      { label: "Interactive Report", href: "/interactive-report", icon: "interactiveReport" },
      { label: "Chat with DB", href: "/chat-with-db", icon: "chatWithDb" },
      { label: "Schedule Management", href: "/schedule-management", icon: "scheduleManagement" },
      { label: "Configuration", href: "/configuration", icon: "configuration" },
    ],
  },
];
