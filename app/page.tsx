import Keycaps from "@/components/Keycaps";
import MenuBar from "@/components/MenuBar";
import ProjectBrowser from "@/components/ProjectBrowser";
import Window from "@/components/Window";
import { experience, personalInfo } from "@/data/resume";

const facts = [
  { label: "Day job", value: "Software engineer, Marriott International" },
  { label: "Education", value: "MS Information Systems Management, BYU" },
  { label: "Before that", value: "Guitarist and pianist in Ritt Momney" },
  { label: "Location", value: personalInfo.location },
];

const contacts = [
  { label: "Email me", href: `mailto:${personalInfo.email}` },
  { label: "GitHub", href: personalInfo.github },
  { label: "LinkedIn", href: personalInfo.linkedin },
];

export default function Home() {
  const intro = (
    <>
      <div className="logo-panel">
        <Keycaps />
        <div className="logo-text">
          <h1>Christopher Kearl</h1>
          <p>I automate compliance at work. These are the things I build after hours.</p>
        </div>
      </div>
      <dl className="about-facts">
        {facts.map((fact) => (
          <div key={fact.label}>
            <dt>{fact.label}:</dt>
            <dd>{fact.value}</dd>
          </div>
        ))}
      </dl>
    </>
  );

  return (
    <>
      <MenuBar />
      <main className="desktop">
        <ProjectBrowser intro={intro} />
        <div className="lower-windows">
          <Window title="Work History" id="work" className="work-window">
            <ul className="work-list">
              {experience.map((job) => (
                <li key={job.id}>
                  <div>
                    <strong>{job.title}</strong>
                    <span>{job.company}</span>
                  </div>
                  <span className="work-dates">{job.duration}</span>
                </li>
              ))}
            </ul>
          </Window>
          <Window title="Contact" id="contact" className="contact-window">
            <p>The fastest way to reach me is email.</p>
            <div className="info-links">
              {contacts.map((contact) => (
                <a key={contact.label} href={contact.href} className="gel-button">
                  {contact.label}
                </a>
              ))}
            </div>
          </Window>
        </div>
      </main>
    </>
  );
}
