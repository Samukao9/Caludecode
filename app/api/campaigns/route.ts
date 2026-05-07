import { prisma } from "@/lib/prisma";
import { NextResponse } from "next/server";

export async function GET() {
  const campaigns = await prisma.campaign.findMany({ orderBy: { sentAt: "desc" } });
  return NextResponse.json({ campaigns });
}
