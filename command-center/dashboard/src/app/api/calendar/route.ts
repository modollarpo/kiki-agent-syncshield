import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const user = searchParams.get("user") || "user";

  return NextResponse.json({
    user,
    events: ["Ops review (in 1h)", "Security audit (tomorrow)"],
  });
}
