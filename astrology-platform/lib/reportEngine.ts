import OpenAI from "openai";
import { z } from "zod";
import { buildAstrologyPrompt } from "./prompt";
import { AstrologyReport, BirthDetails } from "./types";

const sectionSchema = z.object({
  title: z.string(),
  body: z.string()
});

const reportSchema = z.object({
  basicDetails: sectionSchema,
  personality: sectionSchema,
  career: sectionSchema,
  love: sectionSchema,
  wealth: sectionSchema,
  dasha: sectionSchema,
  futurePredictions: sectionSchema,
  remedies: sectionSchema
});

export async function generateAstrologyReport(details: BirthDetails): Promise<AstrologyReport> {
  if (!process.env.OPENAI_API_KEY) {
    return demoReport(details);
  }

  const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
  const completion = await client.chat.completions.create({
    model: process.env.OPENAI_MODEL || "gpt-4o-mini",
    temperature: 0.72,
    response_format: { type: "json_object" },
    messages: [
      {
        role: "system",
        content: "You create careful, non-alarmist Vedic astrology reports in strict JSON."
      },
      { role: "user", content: buildAstrologyPrompt(details) }
    ]
  });

  const raw = completion.choices[0]?.message?.content;
  if (!raw) throw new Error("The astrology model returned an empty response.");

  return reportSchema.parse(JSON.parse(raw));
}

export function makePersonalityPreview(text: string) {
  const words = text.split(/\s+/);
  const cutoff = Math.max(70, Math.floor(words.length * 0.45));
  const preview = words.slice(0, cutoff).join(" ");
  return `${preview.trim()}...`;
}

function demoReport(details: BirthDetails): AstrologyReport {
  const firstName = details.fullName.trim().split(/\s+/)[0] || "Native";
  return {
    basicDetails: {
      title: "Basic Details",
      body: `${details.fullName} was born on ${details.dob} at ${details.time} in ${details.place}. This reading uses the birth details as the foundation for a Vedic-style Janma Kundli interpretation, focusing on temperament, opportunity patterns, timing themes, and practical remedies. For production-grade precision, connect a Panchang or ephemeris engine to calculate exact lagna, nakshatra, and divisional charts.`
    },
    personality: {
      title: "Personality & Life Path",
      body: `${firstName}, your chart pattern suggests a mind that is observant, emotionally intelligent, and quietly ambitious. You are likely to notice subtle shifts in people and environments before others do, which makes you good at reading situations and choosing the right moment to act. Your life path carries a strong theme of self-definition: early phases may feel like you are meeting expectations, but your real growth begins when you stop asking for permission to want what you want. There is also a karmic emphasis on communication, learning, and service. When you speak with clarity, teach, advise, write, design, or organize complex ideas, your natural magnetism becomes stronger. The most important turning point appears when you begin to trust your inner timing instead of comparing your pace with others. This is where your chart becomes especially interesting, because it indicates a period where one personal decision can reshape both identity and direction in a visible way.`
    },
    career: {
      title: "Career",
      body: `Professionally, the strongest indications favor roles where analysis, guidance, creativity, and responsibility meet. You may do well in product, consulting, education, design, research, operations, healing-oriented work, finance, or technology-enabled services. Your chart rewards skill depth over shortcuts. Recognition is more likely when you build a distinctive voice and become known for dependable judgment. Avoid career paths that require you to suppress intuition for too long.`
    },
    love: {
      title: "Love & Relationships",
      body: `In relationships, you need emotional safety, consistency, and respect for your independence. You may seem composed on the outside while feeling deeply inside, so partners who rely only on surface signals may misunderstand you. The chart favors mature bonds formed through trust, shared purpose, and honest conversation. The key lesson is to avoid over-functioning for people who have not shown equal commitment.`
    },
    wealth: {
      title: "Wealth & Financial Pattern",
      body: `Your wealth pattern improves through planned growth, repeatable systems, and patient asset-building. Sudden speculation is less favorable than disciplined accumulation. Income can rise when you package your knowledge into a valuable service or product. Money decisions should be reviewed when emotions are high, because the chart shows generosity and urgency can sometimes override strategy.`
    },
    dasha: {
      title: "Dasha & Major Life Cycles",
      body: `The dasha themes point toward alternating phases of inner preparation and public movement. During preparation cycles, you may feel delayed, but skills and emotional maturity are being consolidated. During movement cycles, the same preparation can turn into visible opportunity. A precise Vimshottari dasha requires exact Moon nakshatra calculation; this reading treats timing as interpretive until ephemeris data is connected.`
    },
    futurePredictions: {
      title: "Future Predictions",
      body: `The next meaningful phase favors clearer boundaries, professional refinement, and a more confident personal identity. A new collaboration, role, or learning path may become important when it aligns with long-term stability rather than temporary validation. The chart encourages saying yes to opportunities that expand responsibility without draining your health or self-respect.`
    },
    remedies: {
      title: "Remedies",
      body: `Begin Thursdays with a simple gratitude practice and one act of guidance or generosity. Keep a consistent sleep rhythm around major decisions. Chanting “Om Gurave Namah” 108 times on Thursdays, donating yellow food items, and maintaining a clean study or work space can support clarity. Remedies work best as grounding rituals, not as substitutes for action.`
    }
  };
}
