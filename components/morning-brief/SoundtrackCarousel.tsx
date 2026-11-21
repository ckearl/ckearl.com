"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { Soundtrack } from "@/lib/morning-brief/types";

const ADVANCE_MS = 5000;

// Swipe or use the arrows and dots. Moves on every 5 seconds unless it's paused, hovered or focused.
export default function SoundtrackCarousel({ picks }: { picks: Soundtrack[] }) {
  const trackRef = useRef<HTMLDivElement>(null);
  const [current, setCurrent] = useState(0);
  const [paused, setPaused] = useState(false);
  const [holding, setHolding] = useState(false);

  const go = useCallback((index: number) => {
    const track = trackRef.current;
    if (!track) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    track.scrollTo({ left: index * track.clientWidth, behavior: reduce ? "auto" : "smooth" });
  }, []);

  useEffect(() => {
    if (paused || holding || picks.length < 2) return;
    const timer = window.setTimeout(() => go((current + 1) % picks.length), ADVANCE_MS);
    return () => window.clearTimeout(timer);
  }, [current, paused, holding, picks.length, go]);

  const onScroll = () => {
    const track = trackRef.current;
    if (track) setCurrent(Math.round(track.scrollLeft / track.clientWidth));
  };

  return (
    <div
      className="soundtrack-carousel"
      aria-roledescription="carousel"
      aria-label="Today's soundtrack picks"
      onMouseEnter={() => setHolding(true)}
      onMouseLeave={() => setHolding(false)}
      onFocus={() => setHolding(true)}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget)) setHolding(false);
      }}
      onTouchStart={() => setHolding(true)}
      onTouchEnd={() => setHolding(false)}
    >
      <div className="soundtrack-track" ref={trackRef} onScroll={onScroll} aria-live={paused || holding ? "polite" : "off"}>
        {picks.map((pick, index) => (
          <article
            key={`${pick.title}-${pick.artist}`}
            className="soundtrack-slide"
            aria-roledescription="slide"
            aria-label={`${index + 1} of ${picks.length}`}
            aria-hidden={index !== current}
            inert={index !== current}
          >
            <p className="muted">{pick.kind}</p>
            <p className="soundtrack-title">{pick.title}</p>
            <p>
              <strong>{pick.artist}</strong>
            </p>
            <p>{pick.why}</p>
            <div className="info-links">
              <a href={pick.url} className="gel-button">
                Open in Spotify
              </a>
            </div>
          </article>
        ))}
      </div>
      {picks.length > 1 && (
        <div className="soundtrack-controls">
          <button type="button" aria-label="Previous pick" onClick={() => go((current - 1 + picks.length) % picks.length)}>
            ‹
          </button>
          <div className="soundtrack-dots">
            {picks.map((pick, index) => (
              <button
                key={`${pick.title}-${pick.artist}`}
                type="button"
                aria-label={`Pick ${index + 1}: ${pick.title}`}
                aria-current={index === current}
                onClick={() => go(index)}
              />
            ))}
          </div>
          <button type="button" aria-label="Next pick" onClick={() => go((current + 1) % picks.length)}>
            ›
          </button>
          <button type="button" className="soundtrack-pause" onClick={() => setPaused(!paused)}>
            {paused ? "Play" : "Pause"}
          </button>
        </div>
      )}
    </div>
  );
}
