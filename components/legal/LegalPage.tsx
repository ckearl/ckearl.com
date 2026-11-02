import AsciiDesktop from "@/components/legal/AsciiDesktop";
import Window from "@/components/new-design/Window";
import { personalInfo } from "@/data/resume";

export default function LegalPage({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <AsciiDesktop>
      <Window title={title} className="legal-window">
        {children}
        <p>
          Questions? Email me at <a href={`mailto:${personalInfo.email}`}>{personalInfo.email}</a>.
        </p>
        <p className="legal-date">Christopher Kearl. Last updated November 1, 2026.</p>
      </Window>
    </AsciiDesktop>
  );
}
