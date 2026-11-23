"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  ["/", "InfraWatch"],
  ["/incidents", "Incidents"],
  ["/drafts", "Drafts"],
  ["/telemetry", "Telemetry"],
  ["/logs", "Logs"],
  ["/login", "Sign in"],
  ["/admin/access-requests", "Access requests"],
  ["/admin/sla", "SLA policy"],
] as const;

/** The primary links; the one for the current page, or the section it is in, is marked. */
export function NavLinks({ path }: { path: string | null }) {
  return (
    <nav className="site-nav" aria-label="Primary">
      {/* shortcut: one row that wraps; collapse into a popover menu when it no longer fits phones */}
      <ul>
        {LINKS.map(([href, label]) => {
          const current = path === href ? "page" : href !== "/" && path?.startsWith(`${href}/`);
          return (
            <li key={href}>
              <Link href={href} aria-current={current || undefined}>
                {label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

export function CurrentNav() {
  return <NavLinks path={usePathname()} />;
}
