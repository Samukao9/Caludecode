import { getJob } from "@/lib/send-engine";
import { NextResponse } from "next/server";

export async function GET(_: Request, { params }: { params: { id: string } }) {
  const job = getJob(params.id);
  if (!job) {
    return NextResponse.json({ error: "Campanha não encontrada." }, { status: 404 });
  }

  const { cancel, ...safeJob } = job;
  return NextResponse.json({ status: safeJob });
}
