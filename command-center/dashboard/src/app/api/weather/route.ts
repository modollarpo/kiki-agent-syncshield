import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const location = searchParams.get("location") || "Unknown";

  return NextResponse.json({
    location,
    temp: "72",
    desc: "Clear (demo)",
  });
}
