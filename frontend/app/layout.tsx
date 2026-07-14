import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Customer Development System",
  description: "Keyword-driven B2B customer development research workspace"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
