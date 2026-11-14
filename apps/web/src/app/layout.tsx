import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "InfraWatch",
  description:
    "Unified observability, incident management and root cause analysis.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
