import type { Metadata } from "next";
import { Noto_Sans, Noto_Sans_KR, Pixelify_Sans } from "next/font/google";
import "../../(new-design)/new-design/globals.css";
import "./brief.css";

const notoSans = Noto_Sans({ subsets: ["latin"], variable: "--font-body", display: "swap" });
const notoSansKr = Noto_Sans_KR({ subsets: ["latin"], variable: "--font-korean", display: "swap", preload: false });
const pixelify = Pixelify_Sans({ subsets: ["latin"], variable: "--font-chrome", display: "swap" });

export const metadata: Metadata = {
  title: "Morning Brief",
  robots: { index: false, follow: false },
};

export default function BriefLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${notoSans.variable} ${notoSansKr.variable} ${pixelify.variable}`}>
      <body>{children}</body>
    </html>
  );
}
