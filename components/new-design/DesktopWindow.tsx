"use client";

import { useId, useLayoutEffect, useState } from "react";

const STORAGE_KEY = "desktop-minimized";

function minimizedTitles(): string[] {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "[]");
  } catch {
    return [];
  }
}

export default function DesktopWindow({
  title,
  className = "",
  children,
}: {
  title: string;
  className?: string;
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
    <section
      className={`window desktop-window ${className} ${minimized ? "is-minimized" : ""}`}
      aria-label={title}
    >
      <div className="window-title">
        <button
          type="button"
          className="window-box"
          aria-label={`${minimized ? "Expand" : "Minimize"} ${title}`}
          aria-expanded={!minimized}
          aria-controls={bodyId}
          onClick={toggle}
        />
        <h2>{title}</h2>
      </div>
      <div id={bodyId} className="window-body" hidden={minimized}>
        {children}
      </div>
    </section>
  );
}
