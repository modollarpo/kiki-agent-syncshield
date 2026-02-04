import { NextResponse } from "next/server";

export async function GET() {
  // Lightweight local/dev health used by the command-center UI.
  // When running the full stack in Docker, prefer gateway aggregation.
  return NextResponse.json({ cpu: 12, mem: 38, disk: 54 });
}
