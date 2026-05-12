"use client";

import { FormEvent, useMemo, useState } from "react";
import { AstrologyReport, AstrologySection, PreviewResponse } from "@/lib/types";

declare global {
  interface Window {
    Razorpay?: new (options: Record<string, unknown>) => { open: () => void };
  }
}

const places = [
  "Mumbai, Maharashtra, India",
  "Delhi, India",
  "Bengaluru, Karnataka, India",
  "Hyderabad, Telangana, India",
  "Chennai, Tamil Nadu, India",
  "Kolkata, West Bengal, India",
  "Pune, Maharashtra, India",
  "Ahmedabad, Gujarat, India",
  "Jaipur, Rajasthan, India",
  "Lucknow, Uttar Pradesh, India"
];

const lockedSamples = {
  career:
    "Your professional chart indicates a field where timing, responsibility, and public trust become important...",
  love:
    "Your relationship pattern shows a deep need for emotional maturity, loyalty, and a partner who respects your inner rhythm...",
  wealth:
    "Your financial growth strengthens when disciplined planning meets a skill that others already trust you for...",
  dasha:
    "The coming life cycles reveal alternating phases of preparation and visible movement, especially around identity and duty...",
  futurePredictions:
    "A meaningful turning point is indicated when one clear decision changes the way people perceive your direction...",
  remedies:
    "The most supportive remedies are simple, consistent, and tied to clarity, generosity, and self-command..."
};

export default function AstroApp() {
  const [form, setForm] = useState({
    fullName: "",
    dob: "",
    time: "",
    place: ""
  });
  const [preview, setPreview] = useState<PreviewResponse | null>(null);
  const [fullReport, setFullReport] = useState<AstrologyReport | null>(null);
  const [reportHtml, setReportHtml] = useState("");
  const [loading, setLoading] = useState(false);
  const [paying, setPaying] = useState(false);
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  const isUnlocked = Boolean(fullReport);

  const reportSections = useMemo(() => {
    if (fullReport) {
      return [
        fullReport.basicDetails,
        fullReport.personality,
        fullReport.career,
        fullReport.love,
        fullReport.wealth,
        fullReport.dasha,
        fullReport.futurePredictions,
        fullReport.remedies
      ];
    }

    if (!preview) return [];

    return [
      preview.basicDetails,
      { title: "Personality & Life Path", body: preview.personalityPreview },
      { title: "Career", body: lockedSamples.career },
      { title: "Love & Relationships", body: lockedSamples.love },
      { title: "Wealth & Financial Pattern", body: lockedSamples.wealth },
      { title: "Dasha & Major Life Cycles", body: lockedSamples.dasha },
      { title: "Future Predictions", body: lockedSamples.futurePredictions },
      { title: "Remedies", body: lockedSamples.remedies }
    ];
  }, [fullReport, preview]);

  async function submitBirthDetails(event: FormEvent) {
    event.preventDefault();
    setError("");
    setStatus("");
    setLoading(true);

    try {
      const response = await fetch("/api/generate-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form)
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Unable to generate report.");
      setPreview(data);
      setFullReport(null);
      setTimeout(() => document.getElementById("report")?.scrollIntoView({ behavior: "smooth" }), 120);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  async function unlockReport() {
    if (!preview) return;
    setPaying(true);
    setError("");
    setStatus("");

    try {
      const orderResponse = await fetch("/api/payment/create-order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reportId: preview.reportId })
      });
      const order = await orderResponse.json();
      if (!orderResponse.ok) throw new Error(order.error || "Unable to start payment.");

      if (order.demo) {
        await verifyPayment({
          orderId: order.id,
          paymentId: `pay_demo_${Date.now()}`,
          signature: "demo_signature"
        });
        return;
      }

      await loadRazorpay();

      const checkout = new window.Razorpay!({
        key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID,
        amount: order.amount,
        currency: "INR",
        name: "urdestiny",
        description: "Full Vedic Astrology Report",
        order_id: order.id,
        handler: async (payment: {
          razorpay_order_id: string;
          razorpay_payment_id: string;
          razorpay_signature: string;
        }) => {
          await verifyPayment({
            orderId: payment.razorpay_order_id,
            paymentId: payment.razorpay_payment_id,
            signature: payment.razorpay_signature
          });
        },
        prefill: { name: form.fullName },
        theme: { color: "#f5c86a" }
      });

      checkout.open();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Payment failed.");
      setPaying(false);
    }
  }

  async function verifyPayment(payload: { orderId: string; paymentId: string; signature: string }) {
    if (!preview) return;
    const response = await fetch("/api/payment/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reportId: preview.reportId, ...payload })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Payment verification failed.");
    setFullReport(data.report);
    setReportHtml(data.html);
    setStatus("Payment successful. Your full report is unlocked.");
    setPaying(false);
  }

  async function sendEmail(event: FormEvent) {
    event.preventDefault();
    if (!preview) return;
    setStatus("");
    setError("");

    try {
      const response = await fetch("/api/email-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reportId: preview.reportId, email })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Unable to send email.");
      setStatus(data.demo ? data.message : "The full report has been sent to your email.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to send email.");
    }
  }

  async function downloadPdf() {
    if (!fullReport) return;
    const { jsPDF } = await import("jspdf");
    const doc = new jsPDF({ unit: "pt", format: "a4" });
    const margin = 44;
    let y = 56;
    doc.setFont("helvetica", "bold");
    doc.setFontSize(22);
    doc.text("Vedic Astrology Report", margin, y);
    y += 28;
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.text(`${form.fullName} | ${form.dob} | ${form.time} | ${form.place}`, margin, y);
    y += 30;

    reportSections.forEach((section) => {
      y = addSectionToPdf(doc, section, y);
    });

    doc.save(`${form.fullName || "vedic"}-astrology-report.pdf`);
  }

  return (
    <main className="app-shell">
      <div className="star-scene" />
      <div className="container">
        <nav className="nav">
          <div className="brand">
            <span className="brand-mark">✦</span>
            <span>urdestiny</span>
          </div>
          <span className="nav-pill">₹99 full unlock</span>
        </nav>

        <section className="hero">
          <div>
            <div className="eyebrow">Vedic Janma Kundli Insights</div>
            <h1>Discover Your True Life Path Through Vedic Astrology</h1>
            <p className="hero-copy">
              Enter your birth details and receive a personalized, structured report with a focused preview before unlocking the complete reading.
            </p>
            <div className="hero-actions">
              <a className="primary-button" href="#generate">Generate Your Report</a>
              <a className="secondary-button" href="#report">View Preview</a>
            </div>
          </div>

          <div className="astro-visual" aria-hidden="true">
            <span className="planet" />
            <span className="planet" />
            <span className="planet" />
          </div>
        </section>

        <section className="form-section" id="generate">
          <div className="section-heading">
            <h2>Your Birth Details</h2>
            <p>Precision matters in astrology. Add your date, time, and birthplace so the report can reflect your personal chart themes.</p>
          </div>

          <form className="birth-form" onSubmit={submitBirthDetails}>
            <div className="field full">
              <label htmlFor="fullName">Full Name</label>
              <input id="fullName" required value={form.fullName} onChange={(event) => setForm({ ...form, fullName: event.target.value })} placeholder="Aarav Sharma" />
            </div>
            <div className="field">
              <label htmlFor="dob">Date of Birth</label>
              <input id="dob" required type="date" value={form.dob} onChange={(event) => setForm({ ...form, dob: event.target.value })} />
            </div>
            <div className="field">
              <label htmlFor="time">Time of Birth</label>
              <input id="time" required type="time" value={form.time} onChange={(event) => setForm({ ...form, time: event.target.value })} />
            </div>
            <div className="field full">
              <label htmlFor="place">Place of Birth</label>
              <input id="place" required list="places" value={form.place} onChange={(event) => setForm({ ...form, place: event.target.value })} placeholder="Mumbai, Maharashtra, India" />
              <datalist id="places">
                {places.map((place) => (
                  <option key={place} value={place} />
                ))}
              </datalist>
            </div>
            <div className="form-footer">
              {loading ? (
                <div className="loader"><span className="loader-dot" />Analyzing planetary positions...</div>
              ) : (
                <span className="microcopy">Preview includes basic details and a partial life path reading.</span>
              )}
              <button className="primary-button" disabled={loading} type="submit">
                {loading ? "Generating..." : "Generate Report"}
              </button>
            </div>
          </form>
          {error && <p className="error">{error}</p>}
        </section>

        <section className="report-section" id="report">
          <div className="section-heading">
            <h2>{preview ? "Your Astrology Report" : "Report Preview"}</h2>
            <p>{preview ? "Your chart reveals a critical turning point in your life path..." : "Generate your report to see the personalized preview here."}</p>
          </div>

          {reportSections.length > 0 && (
            <>
              <div className="report-grid">
                {reportSections.map((section, index) => (
                  <ReportCard key={section.title} section={section} locked={!isUnlocked && index > 1} />
                ))}
              </div>

              {!isUnlocked && (
                <div className="unlock-bar">
                  <div>
                    <strong>Unlock Full Report for ₹99</strong>
                    <span>Your chart reveals a critical turning point in your life path...</span>
                  </div>
                  <button className="primary-button" disabled={paying} onClick={unlockReport}>
                    {paying ? "Unlocking..." : "Pay ₹99 & Unlock"}
                  </button>
                </div>
              )}

              {isUnlocked && (
                <div className="email-panel">
                  <h3>Full report unlocked</h3>
                  <div className="unlock-actions">
                    <button className="secondary-button" onClick={downloadPdf}>Download as PDF</button>
                    {reportHtml && (
                      <button className="ghost-button" onClick={() => openPrintableReport(reportHtml)}>Open Print View</button>
                    )}
                  </div>
                  <form className="email-row" onSubmit={sendEmail}>
                    <input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" />
                    <button className="primary-button" type="submit">Get Full Report on Email</button>
                  </form>
                </div>
              )}
            </>
          )}

          {status && <p className="status">{status}</p>}
        </section>
      </div>
    </main>
  );
}

function ReportCard({ section, locked }: { section: AstrologySection; locked: boolean }) {
  return (
    <article className="report-card">
      <div className={locked ? "locked-content" : ""}>
        <h3>{section.title}</h3>
        <p>{section.body}</p>
      </div>
      {locked && (
        <div className="lock-overlay">
          <div>
            <strong>Unlock Full Report for ₹99</strong>
            <span>Reveal the complete {section.title.toLowerCase()} reading.</span>
          </div>
        </div>
      )}
    </article>
  );
}

function loadRazorpay() {
  return new Promise<void>((resolve, reject) => {
    if (window.Razorpay) return resolve();
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("Unable to load Razorpay checkout."));
    document.body.appendChild(script);
  });
}

function addSectionToPdf(doc: import("jspdf").jsPDF, section: AstrologySection, startY: number) {
  const margin = 44;
  let y = startY;
  if (y > 720) {
    doc.addPage();
    y = 56;
  }
  doc.setFont("helvetica", "bold");
  doc.setFontSize(14);
  doc.text(section.title, margin, y);
  y += 18;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(10.5);
  const lines = doc.splitTextToSize(section.body, 506);
  lines.forEach((line: string) => {
    if (y > 760) {
      doc.addPage();
      y = 56;
    }
    doc.text(line, margin, y);
    y += 15;
  });
  return y + 14;
}

function openPrintableReport(html: string) {
  const win = window.open("", "_blank");
  if (!win) return;
  win.document.write(html);
  win.document.close();
}
