import { prisma } from "@/lib/prisma";
import { NextRequest, NextResponse } from "next/server";

export async function GET() {
  const templates = await prisma.template.findMany({ orderBy: { createdAt: "desc" } });
  return NextResponse.json({ templates });
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  if (!body.name || !body.subject || !body.body) {
    return NextResponse.json({ error: "Nome, assunto e conteúdo são obrigatórios." }, { status: 400 });
  }

  const template = await prisma.template.create({
    data: {
      name: body.name,
      subject: body.subject,
      body: body.body
    }
  });

  return NextResponse.json({ template });
}
