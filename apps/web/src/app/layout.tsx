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
          <Link href="/telemetry">Telemetry</Link>
          <Link href="/logs">Logs</Link>
        </nav>
        {children}
      </body>
    </html>
  );
}
