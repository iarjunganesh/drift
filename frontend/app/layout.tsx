import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DRIFT — Release intelligence for AI infrastructure",
  description: "What changed, why it matters, and what to check next.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
