import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agent Guardian — Live Monitor",
  description: "Real-time AI safety middleware dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
