import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { checkRateLimit } from "@/lib/rateLimit";
import { generateAstrologyReport, makePersonalityPreview } from "@/lib/reportEngine";
import { saveReport } from "@/lib/store";

const inputSchema = z.object({
  fullName: z.string().min(2).max(120),
  dob: z.string().min(4).max(20),
  time: z.string().min(3).max(20),
  place: z.string().min(2).max(160)
});

export async function POST(request: NextRequest) {
  const ip = request.headers.get("x-forwarded-for")?.split(",")[0] || "local";
  const limit = checkRateLimit(ip);

  if (!limit.allowed) {
    return NextResponse.json(
      { error: "Too many free report generations. Please try again later." },
      { status: 429 }
    );
  }

  const parsed = inputSchema.safeParse(await request.json());
  if (!parsed.success) {
    return NextResponse.json({ error: "Please enter valid birth details." }, { status: 400 });
  }

  const report = await generateAstrologyReport(parsed.data);
  const reportId = crypto.randomUUID();
  const personalityPreview = makePersonalityPreview(report.personality.body);

  await saveReport({
    id: reportId,
    user: parsed.data,
    report,
    personalityPreview,
    unlocked: false,
    createdAt: new Date().toISOString()
  });

  return NextResponse.json({
    reportId,
    basicDetails: report.basicDetails,
    personalityPreview,
    lockedSections: [
      "Career",
      "Love",
      "Wealth",
      "Dasha",
      "Future Predictions",
      "Remedies"
    ]
  });
}
