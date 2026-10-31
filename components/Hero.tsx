"use client";

import { useEffect, useRef, useState } from "react";
import PixelIcon, { type IconName } from "@/components/PixelIcon";
import Window from "@/components/Window";
import { personalInfo } from "@/data/resume";
import { AsciiPile } from "@/lib/asciiPile";

const facts = [
  { label: "Day job", value: "Software engineer, Marriott International" },
  { label: "Education", value: "MS Information Systems Management, BYU" },
  { label: "Before that", value: "Guitarist and pianist in Ritt Momney" },
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

// Distance between characters along a drag, in pixels.
const TRAIL_SPACING = 7;
const MAX_TRAIL = 24;
const SPREAD = 10;

export default function Hero() {
  const heroRef = useRef<HTMLElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const pileRef = useRef<AsciiPile | null>(null);
  const [hasPile, setHasPile] = useState(false);

  useEffect(() => {
    const hero = heroRef.current!;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const pile = new AsciiPile(canvasRef.current!, reduceMotion, setHasPile);
    pileRef.current = pile;

    let frame = 0;
    let lastTime = 0;
    let held = false;
    let pointer = { x: 0, y: 0 };

    // Pointer positions stay in viewport coordinates, because the hero moves
    // under a finger while the page scrolls.
    const spawnAt = (x: number, y: number) => {
      const bounds = hero.getBoundingClientRect();
      pile.spawn(
        x - bounds.left + (Math.random() - 0.5) * SPREAD,
        y - bounds.top + (Math.random() - 0.5) * SPREAD
      );
    };

    const run = (time: number) => {
      if (held) spawnAt(pointer.x, pointer.y);
      pile.step(Math.min((time - lastTime) / 1000, 1 / 30));
      pile.draw();
      lastTime = time;
      frame = held || pile.falling ? requestAnimationFrame(run) : 0;
    };

    const wake = () => {
      if (frame) return;
      lastTime = performance.now();
      frame = requestAnimationFrame(run);
    };

    const press = (x: number, y: number) => {
      held = true;
      pointer = { x, y };
      wake();
    };

    const drag = (x: number, y: number) => {
      if (!held) return;
      const distance = Math.hypot(x - pointer.x, y - pointer.y);
      const count = Math.min(Math.ceil(distance / TRAIL_SPACING), MAX_TRAIL);
      for (let index = 1; index <= count; index++) {
        const progress = index / count;
        spawnAt(pointer.x + (x - pointer.x) * progress, pointer.y + (y - pointer.y) * progress);
      }
      pointer = { x, y };
    };

    const release = () => {
      held = false;
    };

    const startsOnControl = (target: EventTarget | null) =>
      target instanceof Element && target.closest("a, button") !== null;

    const onPointerDown = (event: PointerEvent) => {
      if (event.pointerType === "touch" || event.button !== 0) return;
      if (startsOnControl(event.target)) return;
      press(event.clientX, event.clientY);
    };

    const onPointerMove = (event: PointerEvent) => {
      if (event.pointerType !== "touch") drag(event.clientX, event.clientY);
    };

    // Touch events instead of pointer events: the browser sends pointercancel
    // as soon as a touch becomes a scroll, but touchmove keeps arriving. These
    // listeners are passive and never block the scroll.
    const onTouchStart = (event: TouchEvent) => {
      if (startsOnControl(event.target)) return;
      press(event.touches[0].clientX, event.touches[0].clientY);
    };

    const onTouchMove = (event: TouchEvent) => {
      drag(event.touches[0].clientX, event.touches[0].clientY);
    };

    const observer = new ResizeObserver(() => {
      pile.resize(hero.clientWidth, hero.clientHeight);
    });
    observer.observe(hero);

    hero.addEventListener("pointerdown", onPointerDown);
    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", release);
    window.addEventListener("pointercancel", release);
    hero.addEventListener("touchstart", onTouchStart, { passive: true });
    hero.addEventListener("touchmove", onTouchMove, { passive: true });
    hero.addEventListener("touchend", release);
    hero.addEventListener("touchcancel", release);

    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
      hero.removeEventListener("pointerdown", onPointerDown);
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", release);
      window.removeEventListener("pointercancel", release);
      hero.removeEventListener("touchstart", onTouchStart);
      hero.removeEventListener("touchmove", onTouchMove);
      hero.removeEventListener("touchend", release);
      hero.removeEventListener("touchcancel", release);
    };
  }, []);

  return (
    <header className="hero" id="top" ref={heroRef}>
      <canvas className="hero-canvas" ref={canvasRef} aria-hidden="true" />

      <Window title="About Christopher Kearl" className="hero-window">
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
      </Window>

      <Window title="Note Pad" className="note-window">
        {hint}
      </Window>

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
        onClick={() => pileRef.current?.clear()}
      >
        <PixelIcon name={hasPile ? "trashFull" : "trash"} />
        <span>Trash</span>
      </button>
    </header>
  );
}
