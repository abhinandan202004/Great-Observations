import type { Metadata } from "next";
import { Suspense } from "react";
import "./globals.css";
import { CurrentNav, NavLinks } from "./nav";

export const metadata: Metadata = {
  title: "InfraWatch",
  description:
    "Unified observability, incident management and root cause analysis.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en">
      <body>
        <header className="site-header">
          {/* The path is unknown while a page with a dynamic id prerenders: same links, unmarked. */}
          <Suspense fallback={<NavLinks path={null} />}>
            <CurrentNav />
          </Suspense>
        </header>
        {children}
      </body>
    </html>
  );
}
