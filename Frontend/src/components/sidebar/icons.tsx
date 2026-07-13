import type { LucideIcon } from "lucide-react";
import {
  LayoutDashboard,
  BookOpen,
  Activity,
  SquareCheckBig,
  Library,
  Bot,
  Wrench,
  Lightbulb,
  BookMarked,
  Server,
  Database,
  Search,
  FileText,
  MessagesSquare,
  CalendarClock,
  SlidersHorizontal,
  User,
  UserRoundPlus,
  Mail,
  ClipboardList,
  FingerprintPattern,
  Telescope,
} from "lucide-react";

const navIcons: Record<string, LucideIcon> = {
  dashboard: LayoutDashboard,
  playbooks: BookOpen,
  executions: Activity,
  approvals: SquareCheckBig,
  docs: Library,
  agents: Bot,
  tools: Wrench,
  skills: Lightbulb,
  knowledgeBases: BookMarked,
  mcpServers: Server,
  databaseManagement: Database,
  queryOnDatabase: Search,
  interactiveReport: FileText,
  chatWithDb: MessagesSquare,
  scheduleManagement: CalendarClock,
  configuration: SlidersHorizontal,
  users: User,
  teams: UserRoundPlus,
  invitations: Mail,
  auditLog: ClipboardList,
  accessControl: FingerprintPattern,
  observability: Telescope,
};

export function NavIcon({
  name,
  className,
}: {
  name: string;
  className?: string;
}) {
  const Icon = navIcons[name];
  if (!Icon) return null;
  return <Icon className={className} strokeWidth={1.8} />;
}

export function Chevron({
  className,
  direction = "right",
}: {
  className?: string;
  direction?: "right" | "left" | "down" | "up";
}) {
  const points = {
    right: "9 18 15 12 9 6",
    left: "15 18 9 12 15 6",
    down: "6 9 12 15 18 9",
    up: "6 15 12 9 18 15",
  }[direction];

  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <polyline points={points} />
    </svg>
  );
}

export function LogoutIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <polyline points="16 17 21 12 16 7" />
      <line x1="21" y1="12" x2="9" y2="12" />
    </svg>
  );
}
