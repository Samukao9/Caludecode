import { smtpFromBody } from "@/lib/mailer";
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const body = await request.json();
  const required = ["host", "port", "user", "pass", "senderName"];
  for (const key of required) {
    if (!body[key]) {
      return NextResponse.json({ error: `Campo obrigatório: ${key}` }, { status: 400 });
    }
  }

  try {
    const transporter = smtpFromBody({
      host: body.host,
      port: Number(body.port),
      user: body.user,
      pass: body.pass,
      secure: body.secure
    });

    await transporter.sendMail({
      from: `${body.senderName} <${body.user}>`,
      to: body.user,
      subject: "Teste de conexão - DisparoEmailG4",
      text: "Conexão SMTP validada com sucesso.",
      html: "<p>Conexão SMTP validada com sucesso.</p>"
    });

    return NextResponse.json({ ok: true, message: "Teste enviado para o próprio remetente." });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Erro ao testar conexão";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
