"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { navSections } from "./navConfig";
import { NavIcon, Chevron, LogoutIcon } from "./icons";
import { Logo } from "./Logo";
import { logout } from "@/app/(web)/actions";
import { useChatPanel } from "@/components/chat/ChatPanelProvider";

export function Sidebar() {
  const pathname = usePathname();
  const profileInitials = "U";
  const profileName = "User";
  const profileRole = "Member";
  const { open: collapsed } = useChatPanel();
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
    <nav
      className={`flex h-full flex-col overflow-hidden border-r border-line bg-white transition-[width] duration-300 ease-in-out motion-reduce:transition-none ${
        collapsed ? "w-[72px]" : "w-[264px]"
      }`}
    >
      <div
        className={`flex h-[62px] flex-shrink-0 items-center ${
          collapsed ? "justify-center px-2" : "px-5"
        }`}
      >
        <Logo collapsed={collapsed} />
      </div>

      <div className="flex-1 overflow-y-auto overflow-x-hidden px-3 pb-3 pt-1 [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-scrollbar">
        {navSections.map((section) => (
          <div key={section.label ?? "primary"}>
            {section.label && (
              <div className="relative whitespace-nowrap px-2.5 pb-2 pt-[18px] text-[11px] font-bold uppercase tracking-[0.06em] text-ink-muted">
                <span className={collapsed ? "invisible" : undefined}>
                  {section.label}
                </span>
                {collapsed && (
                  <span
                    aria-hidden
                    className="pointer-events-none absolute inset-x-2.5 top-1/2 h-px -translate-y-1/2 bg-line"
                  />
                )}
              </div>
            )}
            {section.items.map((item) => {
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  target={item.newTab ? "_blank" : undefined}
                  rel={item.newTab ? "noopener noreferrer" : undefined}
                  title={collapsed ? item.label : undefined}
                  className={`group relative my-0.5 flex min-h-[38px] items-center gap-2.5 rounded-lg border-l-[3px] py-[9px] pl-3 pr-2.5 text-sm font-medium transition-colors ${
                    active
                      ? "border-accent bg-active font-semibold text-ink"
                      : "border-transparent text-ink-soft hover:bg-hover hover:text-ink"
                  }`}
                >
                  <NavIcon
                    name={item.icon}
                    className={`h-[18px] w-[18px] shrink-0 ${active ? "text-accent" : ""}`}
                  />
                  {!collapsed && (
                    <span className="whitespace-nowrap">{item.label}</span>
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
                title={collapsed ? "Log out" : undefined}
                className={`flex w-full items-center rounded-lg border border-line bg-white text-sm font-medium text-ink-soft shadow-sm transition-colors hover:bg-hover hover:text-ink ${
                  collapsed ? "justify-center px-2 py-2.5" : "gap-2.5 px-3 py-2.5"
                }`}
              >
                <LogoutIcon className="h-[18px] w-[18px] shrink-0" />
                {!collapsed && "Log out"}
              </button>
            </form>
          </div>
        )}
        <button
          type="button"
          onClick={() => setMenuOpen((menu) => !menu)}
          className="flex w-full cursor-pointer items-center gap-2.5 px-3.5 py-3 text-left hover:bg-hover"
        >
          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-[#15171c] text-xs font-bold text-white">
            {profileInitials}
          </div>
          {!collapsed && (
            <>
              <div className="flex flex-col overflow-hidden leading-[1.25]">
                <span className="truncate text-[13.5px] font-semibold text-ink">
                  {profileName}
                </span>
                <span className="whitespace-nowrap text-xs text-ink-muted">
                  {profileRole}
                </span>
              </div>
              <Chevron
                direction={menuOpen ? "up" : "down"}
                className="ml-auto h-4 w-4 flex-shrink-0 text-ink-muted"
              />
            </>
          )}
        </button>
      </div>
    </nav>
  );
}
