import { NextResponse } from "next/server";
import nodemailer from "nodemailer";
import { z } from "zod";
import { reportToHtml } from "@/lib/reportHtml";
import { getReport } from "@/lib/store";

const schema = z.object({
  reportId: z.string().uuid(),
  email: z.string().email()
});

export async function POST(request: Request) {
  const parsed = schema.safeParse(await request.json());
  if (!parsed.success) {
    return NextResponse.json({ error: "Please enter a valid email." }, { status: 400 });
  }

  const report = await getReport(parsed.data.reportId);
  if (!report) return NextResponse.json({ error: "Report not found." }, { status: 404 });
  if (!report.unlocked) {
    return NextResponse.json({ error: "Unlock the report before emailing it." }, { status: 403 });
  }

  const html = reportToHtml(report);

  if (!process.env.SMTP_HOST || !process.env.SMTP_USER || !process.env.SMTP_PASS) {
    return NextResponse.json({
      sent: true,
      demo: true,
      message: "Demo mode: SMTP is not configured, so no email was actually sent."
    });
  }

  const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: Number(process.env.SMTP_PORT || 587),
    secure: Number(process.env.SMTP_PORT || 587) === 465,
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASS
    }
  });

  await transporter.sendMail({
    from: process.env.EMAIL_FROM || "urdestiny <reports@example.com>",
    to: parsed.data.email,
    subject: `Your Vedic Astrology Report, ${report.user.fullName}`,
    html
  });

  return NextResponse.json({ sent: true });
}
