"use client";

import { useId, useLayoutEffect, useState } from "react";

const STORAGE_KEY = "morning-brief-minimized";

function minimizedTitles(): string[] {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "[]");
  } catch {
    return [];
  }
}

export default function BriefWindow({
  title,
  onMove,
  children,
}: {
  title: string;
  onMove?: (by: -1 | 1) => void; // moves the window up or down the page
  children: React.ReactNode;
}) {
  const [minimized, setMinimized] = useState(false);
  const bodyId = useId();

  useLayoutEffect(() => {
    setMinimized(minimizedTitles().includes(title));
  }, [title]);

  const toggle = () => {
    const others = minimizedTitles().filter((saved) => saved !== title);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(minimized ? others : [...others, title]));
    setMinimized(!minimized);
  };

  return (
    <section className={`window brief-window ${minimized ? "is-minimized" : ""}`} aria-label={title}>
      <div className="window-title">
        <button
          type="button"
          className="window-box"
          aria-label={`${minimized ? "Expand" : "Minimize"} ${title}`}
          aria-expanded={!minimized}
          aria-controls={bodyId}
          onClick={toggle}
        />
        {onMove ? (
          <h2
            tabIndex={0}
            aria-description="Drag the title bar, or press the up and down arrows, to move this window"
            onKeyDown={(event) => {
              if (event.key === "ArrowUp" || event.key === "ArrowDown") {
                event.preventDefault();
                onMove(event.key === "ArrowUp" ? -1 : 1);
              }
            }}
          >
            {title}
          </h2>
        ) : (
          <h2>{title}</h2>
        )}
      </div>
      <div id={bodyId} className="window-body" hidden={minimized}>
        {children}
      </div>
    </section>
  );
}
