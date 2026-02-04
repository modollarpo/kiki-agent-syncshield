import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const user = searchParams.get("user") || "user";

  return NextResponse.json({
    user,
    notifications: ["All systems nominal (demo)", "Docker Engine not running"],
  });
}
