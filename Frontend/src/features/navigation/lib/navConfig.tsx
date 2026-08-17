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
      { label: "Docs", href: "/docs", icon: "docs", newTab: true },
    ],
  },
];
