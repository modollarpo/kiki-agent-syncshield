import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    // Forward to SyncPortal FastAPI backend
    const apiUrl = process.env.SYNCPORTAL_API_URL || "http://localhost:8000/impact_audit";
    const res = await fetch(apiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      return NextResponse.json({ error: "SyncPortal API error" }, { status: 500 });
    }
    const data = await res.json();
    return NextResponse.json(data);
  } catch (err: any) {
    return NextResponse.json({ error: err.message || "Unknown error" }, { status: 500 });
  }
}
