import { randomUUID } from "crypto";
import { applyVariables, buildEmailHtml, buildWhatsAppLink, stripHtml } from "@/lib/email";
import { smtpFromBody } from "@/lib/mailer";
import { prisma } from "@/lib/prisma";
import { SendStatus } from "@/lib/types";

const jobs = new Map<string, SendStatus & { cancel: boolean }>();

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export function getJob(id: string) {
  return jobs.get(id);
}

export function stopJob(id: string) {
  const job = jobs.get(id);
  if (!job) return false;
  job.cancel = true;
  return true;
}

export async function startJob(input: {
  recipients: string[];
  subject: string;
  bodyHtml: string;
  senderName: string;
  senderEmail: string;
  replyTo: string;
  unsubscribeEmail: string;
  whatsappNumber: string;
  whatsappCtaText: string;
  whatsappMessage: string;
  smtp: { host: string; port: number; user: string; pass: string; secure?: boolean };
  delayMinMs: number;
  delayMaxMs: number;
}) {
  const id = randomUUID();
  const job: SendStatus & { cancel: boolean } = {
    id,
    total: input.recipients.length,
    sent: 0,
    failed: 0,
    current: "",
    finished: false,
    stopped: false,
    failures: [],
    cancel: false
  };
  jobs.set(id, job);

  const transporter = smtpFromBody(input.smtp);

  (async () => {
    for (const recipient of input.recipients) {
      if (job.cancel) {
        job.stopped = true;
        break;
      }

      job.current = recipient;

      const personalizedBody = applyVariables(input.bodyHtml, recipient);
      const whatsappLink = buildWhatsAppLink(input.whatsappNumber, input.whatsappMessage);

      try {
        const html = buildEmailHtml({
          senderName: input.senderName,
          subject: input.subject,
          bodyHtml: personalizedBody,
          whatsappCtaText: input.whatsappCtaText,
          whatsappLink
        });

        await transporter.sendMail({
          from: `${input.senderName} <${input.senderEmail}>`,
          to: recipient,
          replyTo: input.replyTo,
          subject: input.subject,
          html,
          text: `${stripHtml(personalizedBody)}\n\n${input.whatsappCtaText}: ${whatsappLink}`,
          headers: {
            "List-Unsubscribe": `<mailto:${input.unsubscribeEmail}>`
          }
        });
        job.sent += 1;
      } catch (error) {
        const message = error instanceof Error ? error.message : "Erro desconhecido";
        job.failed += 1;
        job.failures.push({ email: recipient, error: message });
      }

      const min = Math.min(input.delayMinMs, input.delayMaxMs);
      const max = Math.max(input.delayMinMs, input.delayMaxMs);
      const wait = Math.floor(Math.random() * (max - min + 1)) + min;
      await delay(wait);
    }

    job.finished = true;

    await prisma.campaign.create({
      data: {
        subject: input.subject,
        recipientsCount: input.recipients.length,
        successCount: job.sent,
        failureCount: job.failed,
        copyHtml: input.bodyHtml,
        failedEmails: JSON.stringify(job.failures)
      }
    });
  })();

  return id;
}
