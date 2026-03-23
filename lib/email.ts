const EMAIL_REGEX = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;

export function parseEmails(input: string) {
  const chunks = input
    .split(/[\n,;\t]+/)
    .map((item) => item.trim())
    .filter(Boolean);

  const validSet = new Set<string>();
  const invalid = new Set<string>();

  for (const chunk of chunks) {
    const matches = chunk.match(EMAIL_REGEX);
    if (!matches) {
      invalid.add(chunk);
      continue;
    }

    const normalized = matches[0].toLowerCase();
    if (normalized === chunk.toLowerCase()) {
      validSet.add(normalized);
    } else {
      invalid.add(chunk);
    }
  }

  return {
    valid: Array.from(validSet),
    invalid: Array.from(invalid)
  };
}

export function stripHtml(html: string) {
  return html.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();
}

export function applyVariables(body: string, recipientEmail: string) {
  return body.replaceAll("{{EMAIL}}", recipientEmail);
}

export function normalizeWhatsappNumber(number: string) {
  return number.replace(/[^\d]/g, "");
}

export function buildWhatsAppLink(number: string, message: string) {
  return `https://wa.me/${normalizeWhatsappNumber(number)}?text=${encodeURIComponent(message)}`;
}

export function buildEmailHtml({
  senderName,
  subject,
  bodyHtml,
  whatsappCtaText,
  whatsappLink
}: {
  senderName: string;
  subject: string;
  bodyHtml: string;
  whatsappCtaText: string;
  whatsappLink: string;
}) {
  return `
  <div style="margin:0;padding:24px;background:#f4f7fb;font-family:Arial,sans-serif;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:600px;margin:0 auto;background:#ffffff;border-radius:8px;overflow:hidden;">
      <tr>
        <td style="padding:24px;">
          <p style="margin:0 0 8px;font-size:14px;color:#64748b;">${senderName}</p>
          <h1 style="margin:0 0 16px;font-size:22px;color:#0f172a;">${subject}</h1>
          <div style="font-size:15px;line-height:1.6;color:#1e293b;">${bodyHtml}</div>
          <hr style="border:none;border-top:1px solid #e2e8f0;margin:28px 0;" />
          <div style="text-align:center;">
            <a href="${whatsappLink}" style="display:inline-block;background:#25D366;color:#ffffff;text-decoration:none;padding:12px 18px;border-radius:999px;font-weight:bold;">${whatsappCtaText}</a>
          </div>
          <p style="margin:24px 0 0;font-size:12px;color:#94a3b8;text-align:center;">Enviado por ${senderName}</p>
        </td>
      </tr>
    </table>
  </div>`;
}
