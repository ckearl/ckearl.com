import type { Metadata } from "next";
import { Inter, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/ThemeProvider";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Christopher Kearl | Software Engineer & Developer",
  description:
    "Software Engineer specializing in full-stack development, cloud engineering, and compliance automation. Former musician with Ritt Momney. MS in Information Systems Management from BYU.",
  keywords: [
    "Christopher Kearl",
    "Software Engineer",
    "Full-stack Developer",
    "TypeScript",
    "React",
    "Next.js",
    "Python",
    "AWS",
    "Cloud Engineering",
    "Ritt Momney",
  ],
  authors: [{ name: "Christopher Kearl" }],
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://ckearl.com",
    title: "Christopher Kearl | Software Engineer & Developer",
    description:
      "Software Engineer specializing in full-stack development, cloud engineering, and compliance automation.",
    siteName: "Christopher Kearl Portfolio",
  },
  twitter: {
    card: "summary_large_image",
    title: "Christopher Kearl | Software Engineer & Developer",
    description:
      "Software Engineer specializing in full-stack development, cloud engineering, and compliance automation.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${geistMono.variable} font-sans antialiased`}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
