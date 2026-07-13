import type { Metadata } from "next";
import { VT323, IBM_Plex_Mono } from "next/font/google";
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

export const metadata: Metadata = {
  title: "mager-bench",
  description:
    "A personal coding-model benchmark — five tasks scored by an LLM judge, run against Claude Haiku 4.5 and more.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${display.variable} ${mono.variable} h-full`}>
      <body className="h-full font-mono antialiased">{children}</body>
    </html>
  );
}
