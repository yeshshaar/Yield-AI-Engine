import { StoredReport } from "./types";

const orderedKeys = [
  "basicDetails",
  "personality",
  "career",
  "love",
  "wealth",
  "dasha",
  "futurePredictions",
  "remedies"
] as const;

export function reportToHtml(stored: StoredReport) {
  const sections = orderedKeys
    .map((key) => {
      const section = stored.report[key];
      return `<section><h2>${escapeHtml(section.title)}</h2><p>${escapeHtml(section.body)}</p></section>`;
    })
    .join("");

  return `<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Astrology Report - ${escapeHtml(stored.user.fullName)}</title>
    <style>
      body { margin: 0; font-family: Inter, Arial, sans-serif; color: #201b2c; background: #fbf7ef; }
      .page { max-width: 780px; margin: 0 auto; padding: 44px; }
      h1 { font-size: 34px; margin-bottom: 8px; }
      .meta { color: #716579; margin-bottom: 28px; }
      section { border-top: 1px solid #ded2c5; padding: 22px 0; }
      h2 { font-size: 20px; margin: 0 0 10px; color: #6d3de8; }
      p { font-size: 15px; line-height: 1.75; margin: 0; }
    </style>
  </head>
  <body>
    <main class="page">
      <h1>Vedic Astrology Report</h1>
      <div class="meta">${escapeHtml(stored.user.fullName)} · ${escapeHtml(stored.user.dob)} · ${escapeHtml(stored.user.time)} · ${escapeHtml(stored.user.place)}</div>
      ${sections}
    </main>
  </body>
</html>`;
}

function escapeHtml(value: string) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
