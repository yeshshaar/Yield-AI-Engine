import { BirthDetails } from "./types";

export function buildAstrologyPrompt(details: BirthDetails) {
  return `You are an elite Vedic astrologer with 20+ years of experience in Janma Kundli analysis.

Create a highly detailed but easy-to-read Vedic astrology report for the native below.

User Details:
Full Name: ${details.fullName}
Date of Birth: ${details.dob}
Time of Birth: ${details.time}
Place of Birth: ${details.place}

Instructions:
- Use a warm, premium, personal tone.
- Keep language slightly simplified and avoid overly technical jargon.
- Make the report feel specific to the birth details.
- Do not make scary, deterministic, medical, legal, or guaranteed financial claims.
- Use traditional Vedic astrology framing such as lagna, moon sign, nakshatra, planetary strengths, dasha themes, and remedies, but explain them in plain language.
- Avoid fake claims. If exact astronomical calculations are unavailable, say the analysis is interpretive and should be refined with a precise Kundli.
- Output only valid JSON. No markdown fences.

Return exactly this JSON shape:
{
  "basicDetails": { "title": "Basic Details", "body": "..." },
  "personality": { "title": "Personality & Life Path", "body": "..." },
  "career": { "title": "Career", "body": "..." },
  "love": { "title": "Love & Relationships", "body": "..." },
  "wealth": { "title": "Wealth & Financial Pattern", "body": "..." },
  "dasha": { "title": "Dasha & Major Life Cycles", "body": "..." },
  "futurePredictions": { "title": "Future Predictions", "body": "..." },
  "remedies": { "title": "Remedies", "body": "..." }
}`;
}
