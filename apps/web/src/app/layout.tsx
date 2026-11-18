import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "InfraWatch",
  description:
    "Unified observability, incident management and root cause analysis.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en">
      <body>
        <nav aria-label="Main">
          <Link href="/">InfraWatch</Link>
          <Link href="/incidents">Incidents</Link>
          <Link href="/telemetry">Telemetry</Link>
          <Link href="/logs">Logs</Link>
          <Link href="/login">Sign in</Link>
          <Link href="/admin/access-requests">Access requests</Link>
          <Link href="/admin/sla">SLA policy</Link>
        </nav>
        {children}
      </body>
    </html>
  );
}
