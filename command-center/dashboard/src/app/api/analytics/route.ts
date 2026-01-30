import { NextResponse } from "next/server";

export async function GET() {
  try {
    const res = await fetch("http://localhost:8001/analytics");
    if (!res.ok) throw new Error("Failed to fetch analytics");
    const data = await res.json();
    return NextResponse.json({ analytics: data.analytics || [] });
  } catch (e) {
    return NextResponse.json({ analytics: [10, 20, 30, 40, 50, 60, 70, 80, 90, 100] }); // fallback demo data
  }
}
