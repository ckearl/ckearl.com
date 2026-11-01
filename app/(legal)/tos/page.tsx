import type { Metadata } from "next";
import LegalPage from "@/components/legal/LegalPage";

export const metadata: Metadata = { title: "Terms of Service | Morning Brief" };

export default function TermsPage() {
  return (
    <LegalPage title="Terms of Service">
      <p>Morning Brief is a personal project I built for my own use. It isn&apos;t a public service, and nobody else can sign up.</p>
      <p>
        It&apos;s provided as is, with no warranty. Its weather, scores, news and other information come from outside
        sources and may be wrong or out of date.
      </p>
      <p>It may change or stop at any time.</p>
    </LegalPage>
  );
}
