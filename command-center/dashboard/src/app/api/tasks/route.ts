import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const user = searchParams.get("user") || "user";

  return NextResponse.json({
    user,
    tasks: [
      { task: "Review service health", done: false },
      { task: "Verify onboarding audit flow", done: false },
    ],
  });
}
