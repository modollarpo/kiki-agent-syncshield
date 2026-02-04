import { NextResponse } from "next/server";

export async function GET() {
  try {
    const gatewayBase = process.env.KIKI_GATEWAY_URL || "http://localhost:8080";
    const internalKey = process.env.INTERNAL_API_KEY || "";
    const res = await fetch(`${gatewayBase}/api/syncbrain/analytics`, {
      headers: internalKey ? { "x-internal-api-key": internalKey } : undefined,
      cache: "no-store",
    });
    if (!res.ok) throw new Error("Failed to fetch analytics");
    const data = await res.json();
    return NextResponse.json({ analytics: data.analytics || [] });
  } catch (e) {
    return NextResponse.json({
      analytics: [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
      error: e instanceof Error ? e.message : String(e),
    }); // fallback demo data
  }
}
