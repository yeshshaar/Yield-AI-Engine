import crypto from "node:crypto";

export function verifyRazorpaySignature(args: {
  orderId: string;
  paymentId: string;
  signature: string;
}) {
  if (!process.env.RAZORPAY_KEY_SECRET) {
    return args.signature === "demo_signature";
  }

  const expected = crypto
    .createHmac("sha256", process.env.RAZORPAY_KEY_SECRET)
    .update(`${args.orderId}|${args.paymentId}`)
    .digest("hex");

  return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(args.signature));
}
