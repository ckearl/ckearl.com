"use client";

import Image from "next/image";
import { useRef, useState, type KeyboardEvent } from "react";
import PixelIcon from "@/components/new-design/PixelIcon";
import Window from "@/components/new-design/Window";
import { projects } from "@/data/new-design/projects";

const largest = Math.max(...projects.map((project) => project.lines));
const totalLines = projects.reduce((sum, project) => sum + project.lines, 0);

export default function ProjectBrowser() {
  const [selectedId, setSelectedId] = useState(projects[0].id);
  const listRef = useRef<HTMLUListElement>(null);
  const infoRef = useRef<HTMLDivElement>(null);
  const selected = projects.find((project) => project.id === selectedId) ?? projects[0];

  const select = (id: string) => {
    setSelectedId(id);
    // The info window sits under the list on narrow screens.
    if (window.matchMedia("(max-width: 959px)").matches) {
      const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      infoRef.current?.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth" });
    }
  };

  const moveFocus = (event: KeyboardEvent<HTMLUListElement>) => {
    if (event.key !== "ArrowDown" && event.key !== "ArrowUp") return;
    event.preventDefault();
    const buttons = [...(listRef.current?.querySelectorAll("button") ?? [])];
    const index = buttons.indexOf(document.activeElement as HTMLButtonElement);
    const step = event.key === "ArrowDown" ? 1 : -1;
    const next = buttons[(index + step + buttons.length) % buttons.length];
    next?.focus();
    next?.click();
  };

  return (
    <div className="stack">
      <div className="project-list">
        <div className="project-head">
          <span>{projects.length} side projects</span>
          <span>{totalLines.toLocaleString("en-US")} lines I wrote</span>
        </div>
        <ul ref={listRef} onKeyDown={moveFocus}>
          {projects.map((project) => (
            <li key={project.id}>
              <button
                type="button"
                className="project-row"
                aria-current={project.id === selectedId ? "true" : undefined}
                onClick={() => select(project.id)}
              >
                <PixelIcon name={project.icon} />
                <span className="project-text">
                  <strong>{project.name}</strong>
                  <span>{project.summary}</span>
                </span>
                <span className="project-size">
                  {project.lines.toLocaleString("en-US")}
                </span>
                <span className="bar" aria-hidden="true">
                  <span style={{ width: `${(project.lines / largest) * 100}%` }} />
                </span>
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div className="info-slot" ref={infoRef}>
        <Window key={selected.id} title={`${selected.name} Info`} className="info-window">
          <div aria-live="polite">
            <div className="info-heading">
              <PixelIcon name={selected.icon} />
              <div>
                <h3>{selected.name}</h3>
                <p>{selected.status}</p>
              </div>
            </div>
            {selected.image && (
              <div className="info-image">
                <Image
                  src={selected.image.src}
                  alt={selected.image.alt}
                  width={selected.image.width}
                  height={selected.image.height}
                  priority
                />
              </div>
            )}
            <p className="info-details">{selected.details}</p>
            <dl className="info-facts">
              <dt>Built with</dt>
              <dd>{selected.stack.join(", ")}</dd>
            </dl>
            {selected.links.length > 0 ? (
              <div className="info-links">
                {selected.links.map((link) => (
                  <a key={link.href} href={link.href} className="gel-button" target="_blank" rel="noreferrer">
                    {link.label}
                  </a>
                ))}
              </div>
            ) : (
              <p className="info-note">Not public yet.</p>
            )}
          </div>
        </Window>
      </div>
    </div>
  );
}
