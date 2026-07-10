"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { getNavSections } from "./navConfig";
import { NavIcon, Chevron, LogoutIcon } from "./icons";
import { Logo } from "./Logo";
import { logout } from "@/app/(web)/actions";

export function Sidebar({ role }: { role?: string }) {
  const pathname = usePathname();
  const sections = getNavSections(role);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!menuOpen) return;
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [menuOpen]);

  return (
    <nav className="flex h-full w-[264px] flex-col overflow-hidden border-r border-line bg-white">
      <div className="flex flex-shrink-0 items-center px-5 pb-3.5 pt-5">
        <Logo />
      </div>

      <div className="flex-1 overflow-y-auto px-3 pb-3 pt-1 [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-scrollbar">
        {sections.map((section) => (
          <div key={section.label ?? "primary"}>
            {section.label && (
              <div className="px-2.5 pb-2 pt-[18px] text-[11px] font-bold uppercase tracking-[0.06em] text-ink-muted">
                {section.label}
              </div>
            )}
            {section.items.map((item) => {
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`group relative my-0.5 flex items-center gap-2.5 rounded-lg border-l-[3px] py-[9px] pl-3 pr-2.5 text-sm font-medium transition-colors ${
                    active
                      ? "border-accent bg-active font-semibold text-ink"
                      : "border-transparent text-ink-soft hover:bg-hover hover:text-ink"
                  }`}
                >
                  <NavIcon
                    name={item.icon}
                    className={`h-[18px] w-[18px] shrink-0 ${active ? "text-accent" : ""}`}
                  />
                  {item.label}
                  {item.hasChevron && (
                    <Chevron className="ml-auto h-[15px] w-[15px] text-ink-muted opacity-0 transition-opacity group-hover:opacity-100" />
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </div>

      <div ref={menuRef} className="relative flex-shrink-0 border-t border-line">
        {menuOpen && (
          <div className="absolute bottom-full left-0 right-0 p-2">
            <form action={logout}>
              <button
                type="submit"
                className="flex w-full items-center gap-2.5 rounded-lg border border-line bg-white px-3 py-2.5 text-sm font-medium text-ink-soft shadow-sm transition-colors hover:bg-hover hover:text-ink"
              >
                <LogoutIcon className="h-[18px] w-[18px] shrink-0" />
                Log out
              </button>
            </form>
          </div>
        )}
        <button
          type="button"
          onClick={() => setMenuOpen((open) => !open)}
          className="flex w-full cursor-pointer items-center gap-2.5 px-3.5 py-3 text-left hover:bg-hover"
        >
          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-[#15171c] text-xs font-bold text-white">
            DA
          </div>
          <div className="flex flex-col overflow-hidden leading-[1.25]">
            <span className="truncate text-[13.5px] font-semibold text-ink">
              Dev Admin
            </span>
            <span className="text-xs text-ink-muted">Tenant Admin</span>
          </div>
          <Chevron
            direction={menuOpen ? "down" : "left"}
            className="ml-auto h-4 w-4 flex-shrink-0 text-ink-muted"
          />
        </button>
      </div>
    </nav>
  );
}
