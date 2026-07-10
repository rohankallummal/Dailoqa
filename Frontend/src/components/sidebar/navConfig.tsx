export type NavItem = {
  label: string;
  href: string;
  icon: string;
  hasChevron?: boolean;
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
      { label: "Docs", href: "/docs", icon: "docs" },
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
  {
    label: "Admin",
    items: [
      { label: "Users", href: "/users", icon: "users" },
      { label: "Teams", href: "/teams", icon: "teams" },
      { label: "Invitations", href: "/invitations", icon: "invitations" },
      { label: "Audit log", href: "/audit-log", icon: "auditLog" },
      { label: "Access Control", href: "/access-control", icon: "accessControl", hasChevron: true },
      { label: "Observability", href: "/observability", icon: "observability" },
    ],
  },
];

export const adminSectionLabel = "Admin";

export const adminRoutes: string[] =
  navSections
    .find((section) => section.label === adminSectionLabel)
    ?.items.map((item) => item.href) ?? [];

export function getNavSections(role?: string): NavSection[] {
  if (role === "admin") return navSections;
  return navSections.filter((section) => section.label !== adminSectionLabel);
}
