import type { Metadata, Viewport } from "next";
import { Baloo_2, JetBrains_Mono, Lexend } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const display = Baloo_2({ subsets: ["latin"], weight: ["700", "800"], variable: "--font-display", display: "swap" });
const body = Lexend({ subsets: ["latin"], variable: "--font-body", display: "swap" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap" });

export const metadata: Metadata = {
  title: { default: "Tiny Python Projects, tested live", template: "%s · Tiny Python Projects, tested live" },
  description:
    "Little Python toys you can play with, rules that check them, and gremlins that try to sneak past the rules. Everything runs for real in your browser.",
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#d9f1ff" },
    { media: "(prefers-color-scheme: dark)", color: "#0c1a2b" },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable} ${mono.variable}`}>
      <body>
        <a className="skip" href="#main">
          Skip to content
        </a>
        <header className="site-head">
          <Link href="/" className="wordmark">
            <span className="snake" aria-hidden="true">🐍</span>
            Tiny Python Toybox
          </Link>
        </header>
        <main id="main">{children}</main>
        <footer className="site-foot">
          <p>
            Based on <a href="https://www.manning.com/books/tiny-python-projects">Tiny Python Projects</a> by
            Ken Youens-Clark. The tests and input files come from{" "}
            <a href="https://github.com/kyclark/tiny_python_projects">his repository</a> under the MIT
            license and are unchanged. The solutions, real-world tests and this site are mine.
          </p>
        </footer>
      </body>
    </html>
  );
}
