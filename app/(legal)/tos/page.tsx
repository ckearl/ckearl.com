import type { Metadata } from "next";
import LegalPage from "@/components/legal/LegalPage";

export const metadata: Metadata = { title: "Terms of Service | Morning Brief" };

export default function TermsPage() {
  return (
    <LegalPage title="Terms of Service">
      <p>Morning Brief is a personal project for my own use. It isn&apos;t a public service, and it comes with no warranty.</p>
    </LegalPage>
  );
}
