import { NextResponse } from "next/server";
import { z } from "zod";
import { verifyRazorpaySignature } from "@/lib/payment";
import { reportToHtml } from "@/lib/reportHtml";
import { getReport, unlockReport } from "@/lib/store";

const schema = z.object({
  reportId: z.string().uuid(),
  orderId: z.string(),
  paymentId: z.string(),
  signature: z.string()
});

export async function POST(request: Request) {
  const parsed = schema.safeParse(await request.json());
  if (!parsed.success) {
    return NextResponse.json({ error: "Invalid payment verification payload." }, { status: 400 });
  }

  const report = await getReport(parsed.data.reportId);
  if (!report) return NextResponse.json({ error: "Report not found." }, { status: 404 });

  const verified = verifyRazorpaySignature(parsed.data);
  if (!verified) {
    return NextResponse.json({ error: "Payment signature verification failed." }, { status: 401 });
  }

  const unlocked = await unlockReport(parsed.data.reportId, parsed.data.paymentId);
  if (!unlocked) return NextResponse.json({ error: "Unable to unlock report." }, { status: 500 });

  return NextResponse.json({
    unlocked: true,
    report: unlocked.report,
    html: reportToHtml(unlocked)
  });
}
