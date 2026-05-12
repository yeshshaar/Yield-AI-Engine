# urdestiny

A full-stack Next.js astrology product where users generate a Vedic report preview, pay ₹99 through Razorpay, unlock the full report, download it, and email it.

## Run locally

```bash
npm install
npm run dev
```

Open http://localhost:3000.

Without API keys the app uses a realistic demo report and demo payment verification so the full UX can be tested locally. Add values from `.env.example` to enable OpenAI, MongoDB, Razorpay, and SMTP.

## Deploy

Deploy the `astrology-platform` directory as a Next.js app. On Vercel, set the project root directory to `astrology-platform`, then add the environment variables from `.env.example`.

Required production variables:

- `OPENAI_API_KEY`
- `MONGODB_URI`
- `RAZORPAY_KEY_ID`
- `RAZORPAY_KEY_SECRET`
- `NEXT_PUBLIC_RAZORPAY_KEY_ID`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASS`
- `EMAIL_FROM`

## Security notes

- `/api/generate-report` stores the full report server-side and only returns `basicDetails` plus a truncated personality preview.
- `/api/payment/verify` checks the Razorpay signature when Razorpay secrets are configured, then marks the report unlocked.
- `/api/email-report` only sends unlocked reports.
- A simple in-memory IP rate limiter restricts repeated free generations.
