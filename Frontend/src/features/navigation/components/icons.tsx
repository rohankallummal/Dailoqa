import type { LucideIcon } from "lucide-react";
import { LayoutDashboard, BookOpen, Library } from "lucide-react";

const navIcons: Record<string, LucideIcon> = {
  dashboard: LayoutDashboard,
  playbooks: BookOpen,
  docs: Library,
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
