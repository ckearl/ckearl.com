"use client";

import { useRef } from "react";
import DesktopWindow from "@/components/new-design/DesktopWindow";
import PixelIcon, { type IconName } from "@/components/new-design/PixelIcon";
import { personalInfo } from "@/data/resume";
import { useAsciiPile } from "@/lib/useAsciiPile";

const facts = [
  { label: "Day job", value: "Software engineer, Marriott International" },
  { label: "Education", value: "MS Information Systems Management, BYU" },
  { label: "Languages", value: "English, Korean" },
  { label: "Location", value: personalInfo.location },
];

const icons: { label: string; href: string; icon: IconName }[] = [
  { label: "Projects", href: "#projects", icon: "folder" },
  { label: "Experience", href: "#experience", icon: "folder" },
  { label: "About", href: "#about", icon: "folder" },
  { label: "Contact", href: "#contact", icon: "mail" },
];

const hint = (
  <>
    <p className="note-mouse">Click and drag anywhere on the desktop to drop ASCII.</p>
    <p className="note-touch">Drag your finger to drop ASCII.</p>
  </>
);

export default function Hero() {
  const heroRef = useRef<HTMLElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { hasPile, clear } = useAsciiPile(heroRef, canvasRef, "a, button, .window-title");

  return (
    <header className="hero" id="top" ref={heroRef}>
      <canvas className="ascii-canvas" ref={canvasRef} aria-hidden="true" />

      <DesktopWindow id="about" className="hero-window">
        <div className="logo-panel">
          <div className="logo-text">
            <h1>Christopher Kearl</h1>
            <p>I automate compliance at work. These are the things I build after hours.</p>
            <div className="logo-hint">{hint}</div>
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
      </DesktopWindow>

      <DesktopWindow id="note" className="note-window">
        {hint}
      </DesktopWindow>

      <nav className="desktop-icons" aria-label="Sections">
        {icons.map((item) => (
          <a key={item.href} href={item.href} className="desktop-icon">
            <PixelIcon name={item.icon} />
            <span>{item.label}</span>
          </a>
        ))}
      </nav>

      <button
        type="button"
        className="desktop-icon trash"
        aria-label="Trash: clear the ASCII pile"
        onClick={clear}
      >
        <PixelIcon name={hasPile ? "trashFull" : "trash"} />
        <span>Trash</span>
      </button>
    </header>
  );
}
