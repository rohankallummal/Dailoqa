"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { docsSideNav, type DocsSideNavItem } from "../lib/docsNavConfig";
import { LanguageSelect } from "./LanguageSelect";

function NavItem({ item, active }: { item: DocsSideNavItem; active: boolean }) {
  return (
    <Link
      href={item.href}
      aria-current={active ? "page" : undefined}
      className={`block rounded-lg px-3 py-1.5 text-sm transition-colors ${
        active
          ? "bg-accent/10 font-medium text-accent"
          : "text-ink-soft hover:bg-page hover:text-ink"
      }`}
    >
      {item.label}
    </Link>
  );
}

export function DocsSideNav() {
  const pathname = usePathname();
  const section = docsSideNav[pathname.split("/")[2] ?? ""];

  if (!section) return null;

  return (
    <aside className="hidden w-60 flex-shrink-0 border-r border-line bg-page lg:block">
      <div className="sticky top-0 space-y-4 py-6">
        <LanguageSelect />
        <nav className="space-y-1 px-3">
          {section.primary.map((item) => (
            <NavItem
              key={item.label}
              item={item}
              active={pathname === item.href}
            />
          ))}
          <hr className="!my-3 border-line" />
          {section.pages.map((item) => (
            <NavItem
              key={item.label}
              item={item}
              active={pathname === item.href}
            />
          ))}
        </nav>
      </div>
    </aside>
  );
}
