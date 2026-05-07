import { parseEmails } from "@/lib/email";
import { startJob } from "@/lib/send-engine";
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const body = await request.json();
  const required = ["recipientsRaw", "subject", "bodyHtml", "senderName", "senderEmail", "smtp", "whatsappNumber", "whatsappCtaText", "whatsappMessage"];

  for (const key of required) {
    if (!body[key]) {
      return NextResponse.json({ error: `Campo obrigatório: ${key}` }, { status: 400 });
    }
  }

  const parsed = parseEmails(body.recipientsRaw);
  if (parsed.valid.length === 0) {
    return NextResponse.json({ error: "Nenhum e-mail válido foi encontrado." }, { status: 400 });
  }

  const id = await startJob({
    recipients: parsed.valid,
    subject: body.subject,
    bodyHtml: body.bodyHtml,
    senderName: body.senderName,
    senderEmail: body.senderEmail,
    replyTo: body.replyTo || body.senderEmail,
    unsubscribeEmail: body.unsubscribeEmail || body.senderEmail,
    whatsappNumber: body.whatsappNumber,
    whatsappCtaText: body.whatsappCtaText,
    whatsappMessage: body.whatsappMessage,
    smtp: {
      host: body.smtp.host,
      port: Number(body.smtp.port),
      user: body.smtp.user,
      pass: body.smtp.pass,
      secure: Boolean(body.smtp.secure)
    },
    delayMinMs: Number(body.delayMinMs || 3000),
    delayMaxMs: Number(body.delayMaxMs || 5000)
  });

  return NextResponse.json({ id, validCount: parsed.valid.length, invalid: parsed.invalid });
}
