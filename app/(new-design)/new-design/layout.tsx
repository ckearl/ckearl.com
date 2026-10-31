import type { Metadata } from "next";
import { Noto_Sans, Pixelify_Sans } from "next/font/google";
import "./globals.css";

const notoSans = Noto_Sans({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
});

const pixelify = Pixelify_Sans({
  subsets: ["latin"],
  variable: "--font-chrome",
  display: "swap",
});

const description =
  "Side projects by Christopher Kearl, a software engineer in Provo, UT: Hanja Chain, Spotifast, Listening Stats, Memory Graph and more.";

export const metadata: Metadata = {
  metadataBase: new URL("https://ckearl.com"),
  robots: { index: false, follow: false },
  title: "Christopher Kearl | Software Engineer & Developer",
  description,
  keywords: [
    "Christopher Kearl",
    "Software Engineer",
    "Side Projects",
    "TypeScript",
    "React",
    "Next.js",
    "Python",
    "AWS",
    "Ritt Momney",
  ],
  authors: [{ name: "Christopher Kearl" }],
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://ckearl.com/new-design",
    title: "Christopher Kearl | Software Engineer & Developer",
    description,
    siteName: "Christopher Kearl",
  },
  twitter: {
    card: "summary_large_image",
    title: "Christopher Kearl | Software Engineer & Developer",
    description,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${notoSans.variable} ${pixelify.variable}`}>
      <body>{children}</body>
    </html>
  );
}
