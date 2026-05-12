import { NextResponse } from "next/server";
import Razorpay from "razorpay";
import { z } from "zod";
import { getReport } from "@/lib/store";

const schema = z.object({
  reportId: z.string().uuid()
});

export async function POST(request: Request) {
  const parsed = schema.safeParse(await request.json());
  if (!parsed.success) {
    return NextResponse.json({ error: "Missing report id." }, { status: 400 });
  }

  const report = await getReport(parsed.data.reportId);
  if (!report) return NextResponse.json({ error: "Report not found." }, { status: 404 });
  if (report.unlocked) return NextResponse.json({ unlocked: true });

  if (!process.env.RAZORPAY_KEY_ID || !process.env.RAZORPAY_KEY_SECRET) {
    return NextResponse.json({
      id: `order_demo_${parsed.data.reportId}`,
      amount: 9900,
      currency: "INR",
      demo: true
    });
  }

  const razorpay = new Razorpay({
    key_id: process.env.RAZORPAY_KEY_ID,
    key_secret: process.env.RAZORPAY_KEY_SECRET
  });

  const order = await razorpay.orders.create({
    amount: 9900,
    currency: "INR",
    receipt: parsed.data.reportId,
    notes: { reportId: parsed.data.reportId }
  });

  return NextResponse.json(order);
}
