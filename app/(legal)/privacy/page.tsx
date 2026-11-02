import type { Metadata } from "next";
import LegalPage from "@/components/legal/LegalPage";

export const metadata: Metadata = { title: "Privacy Policy | Morning Brief" };

export default function PrivacyPage() {
  return (
    <LegalPage title="Privacy Policy">
      <p>Morning Brief is a private page I built for myself, and I&apos;m its only user.</p>
      <p>
        It reads my own Google Calendar to write my brief, using Amazon Web Services and the Claude API. It can&apos;t
        change anything, and its use of Google data adheres to the{" "}
        <a href="https://developers.google.com/terms/api-services-user-data-policy">Google API Services User Data Policy</a>,
        including the Limited Use requirements.
      </p>
    </LegalPage>
  );
}
