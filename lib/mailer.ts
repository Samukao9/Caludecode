import nodemailer from "nodemailer";

export function smtpFromBody(body: {
  host: string;
  port: number;
  secure?: boolean;
  user: string;
  pass: string;
}) {
  return nodemailer.createTransport({
    host: body.host,
    port: body.port,
    secure: body.secure ?? body.port === 465,
    auth: {
      user: body.user,
      pass: body.pass
    }
  });
}
