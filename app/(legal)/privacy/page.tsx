import type { Metadata } from "next";
import LegalPage from "@/components/legal/LegalPage";

export const metadata: Metadata = { title: "Privacy Policy | Morning Brief" };

export default function PrivacyPage() {
  return (
    <LegalPage title="Privacy Policy">
      <p>Morning Brief is a private page I built for myself at ckearl.com/morning-brief, and I&apos;m its only user.</p>
      <p>
        It has read-only access to my own Google Calendar so it can show the day&apos;s events. It can&apos;t create, change
        or delete anything.
      </p>
      <p>
        Those events are kept in a private database on Amazon Web Services for up to 90 days, behind a password. They
        aren&apos;t sold, shared or used for advertising.
      </p>
      <p>
        Morning Brief&apos;s use of information received from Google APIs adheres to the{" "}
        <a href="https://developers.google.com/terms/api-services-user-data-policy">Google API Services User Data Policy</a>,
        including the Limited Use requirements.
      </p>
      <p>
        Access can be removed at any time from{" "}
        <a href="https://myaccount.google.com/permissions">Google Account permissions</a>.
      </p>
    </LegalPage>
  );
}
