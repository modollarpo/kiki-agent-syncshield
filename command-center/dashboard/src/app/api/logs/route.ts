import { NextResponse } from "next/server";

export async function GET() {
  try {
    const res = await fetch("http://localhost:8001/logs");
    if (!res.ok) throw new Error("Failed to fetch logs");
    const data = await res.json();
    return NextResponse.json({ logs: data.logs || [] });
  } catch (e) {
    return NextResponse.json({ logs: ["Error fetching logs: " + e.message] });
  }
}
