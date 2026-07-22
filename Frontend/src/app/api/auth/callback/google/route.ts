import type { NextRequest } from "next/server";
import { handleGoogleCallback } from "@/features/auth";

export async function GET(request: NextRequest) {
  return handleGoogleCallback(request);
}
