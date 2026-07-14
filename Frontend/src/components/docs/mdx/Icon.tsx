import {
  Ban,
  Circle,
  Database,
  Download,
  ExternalLink,
  Filter,
  Network,
  Plug,
  RefreshCw,
  Rocket,
  SlidersHorizontal,
  Star,
  Terminal,
  User,
  Wand2,
  Zap,
  type LucideIcon,
} from "lucide-react";

const iconMap: Record<string, LucideIcon> = {
  bolt: Zap,
  database: Database,
  sitemap: Network,
  user: User,
  ban: Ban,
  filter: Filter,
  rocket: Rocket,
  adjustments: SlidersHorizontal,
  terminal: Terminal,
  "plug-connected": Plug,
  "external-link": ExternalLink,
  wand: Wand2,
  star: Star,
  refresh: RefreshCw,
  download: Download,
};

function isImagePath(icon: string): boolean {
  return icon.includes("/") || /\.(png|svg|jpg|jpeg|gif|webp)$/i.test(icon);
}

export function Icon({
  icon,
  size = 16,
  className,
}: {
  icon?: string;
  size?: number;
  className?: string;
}) {
  if (!icon || isImagePath(icon)) return null;
  const Glyph = iconMap[icon] ?? Circle;
  return <Glyph size={size} className={className} aria-hidden />;
}
