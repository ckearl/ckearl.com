import Hero from "@/components/new-design/Hero";
import MenuBar from "@/components/new-design/MenuBar";
import ProjectBrowser from "@/components/new-design/ProjectBrowser";
import {
  achievements,
  certifications,
  education,
  experience,
  personalInfo,
  skills,
} from "@/data/resume";

const contacts = [
  { label: "Email me", href: `mailto:${personalInfo.email}` },
  { label: "GitHub", href: personalInfo.github },
  { label: "LinkedIn", href: personalInfo.linkedin },
];

export default function Home() {
  return (
    <>
      <MenuBar />
      <Hero />
      <main>
        <section id="projects" className="section">
          <div className="section-inner">
            <h2 className="section-title">Projects</h2>
            <p className="section-intro">
              What I&apos;m building outside of work. The bars show how many lines of each one I
              wrote.
            </p>
            <ProjectBrowser />
          </div>
        </section>

        <section id="experience" className="section">
          <div className="section-inner">
            <h2 className="section-title">Experience</h2>
            <ol className="job-list">
              {experience.map((job) => (
                <li key={job.id}>
                  <p className="job-dates">{job.duration}</p>
                  <div>
                    <h3>{job.title}</h3>
                    <p className="job-company">
                      {job.company}, {job.location}
                    </p>
                    <p>{job.description}</p>
                    <p className="job-stack">{job.technologies.join(", ")}</p>
                  </div>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section id="skills" className="section">
          <div className="section-inner">
            <h2 className="section-title">Skills</h2>
            <dl className="skill-grid">
              {Object.entries(skills.categories).map(([category, items]) => (
                <div key={category}>
                  <dt>{category}</dt>
                  <dd>{items.join(", ")}</dd>
                </div>
              ))}
            </dl>
          </div>
        </section>

        <section id="about" className="section">
          <div className="section-inner about-grid">
            <div>
              <h2 className="section-title">About</h2>
              <p>
                I&apos;m a software engineer in {personalInfo.location}. At Marriott I&apos;m the
                sole engineer on the compliance and security automation that 30+ internal teams
                rely on. Before that I played guitar and piano in Ritt Momney, and I still end up
                building a lot of tools around music.
              </p>
              <ul className="about-list">
                {achievements.map((achievement) => (
                  <li key={achievement.title}>
                    <h3>{achievement.title}</h3>
                    <p>{achievement.description}</p>
                  </li>
                ))}
              </ul>
            </div>
            <div className="about-side">
              <h3>Education</h3>
              <p>
                {education.degree}
                <br />
                {education.school}
                <br />
                {education.duration}
              </p>
              <h3>Certifications</h3>
              <ul>
                {certifications.map((certification) => (
                  <li key={certification.name}>
                    {certification.name}, {certification.date}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>
      </main>

      <footer id="contact" className="contact">
        <div className="section-inner">
          <h2>Contact</h2>
          <p>The fastest way to reach me is email.</p>
          <div className="info-links">
            {contacts.map((contact) => (
              <a key={contact.label} href={contact.href} className="gel-button">
                {contact.label}
              </a>
            ))}
          </div>
          <p className="copyright">© {new Date().getFullYear()} Christopher Kearl</p>
        </div>
      </footer>
    </>
  );
}
