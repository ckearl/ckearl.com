import type { Metadata } from "next";
import { Noto_Sans, Pixelify_Sans } from "next/font/google";
import "../(new-design)/new-design/globals.css";
import "./legal.css";

const notoSans = Noto_Sans({ subsets: ["latin"], variable: "--font-body", display: "swap" });
const pixelify = Pixelify_Sans({ subsets: ["latin"], variable: "--font-chrome", display: "swap" });

export const metadata: Metadata = {
  metadataBase: new URL("https://ckearl.com"),
  title: "Morning Brief",
};

export default function LegalLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${notoSans.variable} ${pixelify.variable}`}>
      <body>{children}</body>
    </html>
  );
}
