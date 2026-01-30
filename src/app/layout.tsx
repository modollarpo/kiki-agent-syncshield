

"use client";
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { NotificationProvider } from "./notifications";
import Header from "./header";
import { ComplianceEventListener } from "./complianceEvents";
import { SessionProvider } from "next-auth/react";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Only show header on non-login pages
  const pathname = typeof window !== "undefined" ? window.location.pathname : "";
  const showHeader = !pathname.startsWith("/login");
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <SessionProvider>
          <NotificationProvider>
            <ComplianceEventListener />
            {showHeader && <Header />}
            {children}
          </NotificationProvider>
        </SessionProvider>
      </body>
    </html>
  );
}
