import type { Metadata } from "next";
import { VT323, IBM_Plex_Mono } from "next/font/google";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import challengesData from "@/data/challenges.json";
import "./globals.css";

const display = VT323({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-vt323",
});

const mono = IBM_Plex_Mono({
  weight: ["400", "500", "600", "700"],
  subsets: ["latin"],
  variable: "--font-plex-mono",
});

const challengeCount = (challengesData as unknown[]).length;

export const metadata: Metadata = {
  title: "mager-bench",
  description: `A personal coding-model benchmark — ${challengeCount} tasks scored by an LLM judge on correctness, code quality, and documentation.`,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${display.variable} ${mono.variable} h-full`}>
      <body className="flex min-h-full flex-col font-mono antialiased">
        <SiteHeader />
        <main className="flex-1">{children}</main>
        <SiteFooter />
      </body>
    </html>
  );
}
