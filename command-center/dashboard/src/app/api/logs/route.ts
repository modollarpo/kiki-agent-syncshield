import { NextResponse } from "next/server";

export async function GET() {
  try {
    const gatewayBase = process.env.KIKI_GATEWAY_URL || "http://localhost:8080";
    const internalKey = process.env.INTERNAL_API_KEY || "";
    const res = await fetch(`${gatewayBase}/api/syncbrain/logs`, {
      headers: internalKey ? { "x-internal-api-key": internalKey } : undefined,
      cache: "no-store",
    });
    if (!res.ok) throw new Error("Failed to fetch logs");
    const data = await res.json();
    return NextResponse.json({ logs: data.logs || [] });
  } catch (e) {
    const message = e instanceof Error ? e.message : String(e);
    return NextResponse.json({ logs: ["Error fetching logs: " + message] }, { status: 502 });
  }
}
