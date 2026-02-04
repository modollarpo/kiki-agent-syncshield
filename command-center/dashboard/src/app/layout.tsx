"use client";

import "@/app/globals.css";
import { Inter } from "next/font/google";
import { useState } from "react";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState("light");

  return (
    <html lang="en" data-theme={theme}>
      <body className={inter.className + " bg-background min-h-screen flex flex-col"}>
        <header className="bg-card border-b border-border px-6 py-3 flex items-center justify-between">
          <div className="font-bold text-lg">KIKI Agent™ Dashboard</div>
          <button
            className="px-3 py-1 rounded border bg-muted text-muted-foreground text-xs"
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
          >
            {theme === "light" ? "🌙 Dark" : "☀️ Light"}
          </button>
        </header>
        <div className="flex flex-1">
          <aside className="bg-card border-r border-border w-48 p-4 flex flex-col gap-4">
            <a href="/" className="text-sm font-medium hover:text-primary">Home</a>
            <a href="/analytics" className="text-sm font-medium hover:text-primary">Analytics</a>
            <a href="/logs" className="text-sm font-medium hover:text-primary">Neural Log</a>
            <a href="/settings" className="text-sm font-medium hover:text-primary">Settings</a>
          </aside>
          <main className="flex-1 p-6">{children}</main>
        </div>
        <footer className="bg-card border-t border-border px-6 py-2 text-xs text-muted-foreground text-center">
          &copy; {new Date().getFullYear()} KIKI Agent™. All rights reserved.
        </footer>
      </body>
    </html>
  );
}
