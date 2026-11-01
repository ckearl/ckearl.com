"use client";

import Image from "next/image";
import { Fragment, useEffect, useRef } from "react";
import type { Brief, League, Score } from "@/lib/morning-brief/types";

const SPEED = 28; // pixels per second
const RESUME_DELAY = 2500;
const DRAG_THRESHOLD = 5; // pixels a mouse moves before a press stops counting as a click

function Side({ league, team, won }: { league: League; team: Score["home"]; won: boolean }) {
  return (
    <div className={`score-side ${won ? "is-winner" : ""}`}>
      <Image
        src={`/morning-brief/logos/${league}/${team.abbr}.png`}
        alt=""
        width={36}
        height={36}
        unoptimized
        loading="eager"
        draggable={false}
      />
      <span className="score-name">{team.name}</span>
      <span className="score-value">{team.score}</span>
    </div>
  );
}

function Card({ league, game, hidden }: { league: League; game: Score; hidden: boolean }) {
  const content = (
    <>
      <Side league={league} team={game.away} won={game.away.score > game.home.score} />
      <Side league={league} team={game.home} won={game.home.score > game.away.score} />
      <p className="score-status">{game.status}</p>
    </>
  );
  if (!game.url) return <div className="score-card">{content}</div>;
  return (
    <a
      className="score-card"
      href={game.url}
      target="_blank"
      rel="noopener noreferrer"
      draggable={false}
      tabIndex={hidden ? -1 : undefined}
      aria-label={`${game.away.name} ${game.away.score}, ${game.home.name} ${game.home.score}, ${game.status}. Open on ESPN.`}
    >
      {content}
    </a>
  );
}

function Scores({ scores, hidden = false }: { scores: Brief["scores"]; hidden?: boolean }) {
  return scores.map((group) => (
    <Fragment key={group.league}>
      <div className="score-label">
        <strong>{group.label}</strong>
        <span>{group.when}</span>
      </div>
      {group.games.map((game) => (
        <Card key={game.away.abbr} league={group.league} game={game} hidden={hidden} />
      ))}
    </Fragment>
  ));
}

export default function ScoresStrip({ scores }: { scores: Brief["scores"] }) {
  const stripRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const strip = stripRef.current!;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let frame = 0;
    let last = performance.now();
    let position = 0;
    let holding = false;
    let hovering = false;
    let focused = false;
    let pausedUntil = 0;
    let drag: { x: number; left: number } | null = null;
    let pressX = 0;
    let dragged = false;

    // The scores render twice, so jumping back one copy is invisible.
    const copyWidth = () => strip.scrollWidth / 2;

    const wrap = () => {
      const width = copyWidth();
      if (strip.scrollLeft >= width) strip.scrollLeft -= width;
      else if (strip.scrollLeft <= 0) strip.scrollLeft += width;
    };

    const run = (time: number) => {
      const seconds = Math.min((time - last) / 1000, 0.05);
      last = time;
      if (!holding && !hovering && !focused && !reduceMotion && time > pausedUntil) {
        position += SPEED * seconds;
        if (position >= copyWidth()) position -= copyWidth();
        strip.scrollLeft = position;
      } else {
        position = strip.scrollLeft;
      }
      frame = requestAnimationFrame(run);
    };

    const pause = () => {
      pausedUntil = performance.now() + RESUME_DELAY;
    };

    const onPointerDown = (event: PointerEvent) => {
      if (event.pointerType !== "mouse") return;
      holding = true;
      pressX = event.clientX;
      dragged = false;
      drag = { x: event.clientX, left: strip.scrollLeft };
      strip.classList.add("is-dragging");
    };

    const onPointerMove = (event: PointerEvent) => {
      if (!drag) return;
      if (Math.abs(event.clientX - pressX) > DRAG_THRESHOLD) dragged = true;
      strip.scrollLeft = drag.left - (event.clientX - drag.x);
      wrap();
      if (strip.scrollLeft !== drag.left - (event.clientX - drag.x)) {
        drag = { x: event.clientX, left: strip.scrollLeft };
      }
    };

    const onPointerUp = () => {
      if (!drag) return;
      drag = null;
      holding = false;
      strip.classList.remove("is-dragging");
      pause();
    };

    const onClick = (event: MouseEvent) => {
      if (dragged) event.preventDefault();
      dragged = false;
    };

    const onFocusIn = (event: FocusEvent) => {
      focused = (event.target as Element).matches("a:focus-visible");
    };

    const onFocusOut = () => {
      focused = false;
      pause();
    };

    const onTouchStart = () => {
      holding = true;
    };

    const onTouchEnd = () => {
      holding = false;
      pause();
    };

    const onEnter = () => {
      hovering = true;
    };

    const onLeave = () => {
      hovering = false;
    };

    // Covers touch momentum and trackpads, which keep moving after a release.
    const onScroll = () => {
      if (holding || performance.now() < pausedUntil) {
        wrap();
        pause();
      }
    };

    strip.scrollLeft = 1;
    position = 1;
    frame = requestAnimationFrame(run);
    strip.addEventListener("pointerdown", onPointerDown);
    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", onPointerUp);
    strip.addEventListener("click", onClick);
    strip.addEventListener("focusin", onFocusIn);
    strip.addEventListener("focusout", onFocusOut);
    strip.addEventListener("touchstart", onTouchStart, { passive: true });
    strip.addEventListener("touchend", onTouchEnd);
    strip.addEventListener("touchcancel", onTouchEnd);
    strip.addEventListener("mouseenter", onEnter);
    strip.addEventListener("mouseleave", onLeave);
    strip.addEventListener("scroll", onScroll, { passive: true });

    return () => {
      cancelAnimationFrame(frame);
      strip.removeEventListener("pointerdown", onPointerDown);
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", onPointerUp);
      strip.removeEventListener("click", onClick);
      strip.removeEventListener("focusin", onFocusIn);
      strip.removeEventListener("focusout", onFocusOut);
      strip.removeEventListener("touchstart", onTouchStart);
      strip.removeEventListener("touchend", onTouchEnd);
      strip.removeEventListener("touchcancel", onTouchEnd);
      strip.removeEventListener("mouseenter", onEnter);
      strip.removeEventListener("mouseleave", onLeave);
      strip.removeEventListener("scroll", onScroll);
    };
  }, []);

  return (
    <section className="scores" aria-label="Recent scores">
      <div className="scores-track" ref={stripRef} tabIndex={0}>
        <div className="scores-copy">
          <Scores scores={scores} />
        </div>
        <div className="scores-copy" aria-hidden="true">
          <Scores scores={scores} hidden />
        </div>
      </div>
    </section>
  );
}
