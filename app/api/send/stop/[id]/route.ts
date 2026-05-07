import { stopJob } from "@/lib/send-engine";
import { NextResponse } from "next/server";

export async function POST(_: Request, { params }: { params: { id: string } }) {
  const stopped = stopJob(params.id);
  if (!stopped) {
    return NextResponse.json({ error: "Campanha não encontrada." }, { status: 404 });
  }
  return NextResponse.json({ ok: true });
}
