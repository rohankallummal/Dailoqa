import Image from "next/image";
import {
  Ban,
  Circle,
  Database,
  Filter,
  Network,
  RefreshCw,
  User,
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
  refresh: RefreshCw,
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
  if (!icon) return null;
  if (isImagePath(icon)) {
    return (
      <Image
        src={icon}
        alt=""
        width={size}
        height={size}
        className={className}
        aria-hidden
      />
    );
  }
  const Glyph = iconMap[icon] ?? Circle;
  return <Glyph size={size} className={className} aria-hidden />;
}
