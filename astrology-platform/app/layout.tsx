import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "urdestiny",
  description: "Premium Vedic astrology reports unlocked after Razorpay payment."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
