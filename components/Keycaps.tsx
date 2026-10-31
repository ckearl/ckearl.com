"use client";

import { useEffect, useState } from "react";

const rows = [
  [
    { legend: "C", color: "cream" },
    { legend: "K", color: "ink" },
    { legend: "E", color: "sage" },
    { legend: "A", color: "ink" },
    { legend: "R", color: "cream" },
    { legend: "L", color: "ink" },
  ],
  [
    { legend: ".", color: "ink" },
    { legend: "C", color: "sage" },
    { legend: "O", color: "cream" },
    { legend: "M", color: "ink" },
  ],
];

export default function Keycaps() {
  const [pressed, setPressed] = useState<string | null>(null);

  useEffect(() => {
    const down = (event: KeyboardEvent) => {
      if (event.metaKey || event.ctrlKey || event.altKey) return;
      setPressed(event.key.toUpperCase());
    };
    const up = () => setPressed(null);
    window.addEventListener("keydown", down);
    window.addEventListener("keyup", up);
    return () => {
      window.removeEventListener("keydown", down);
      window.removeEventListener("keyup", up);
    };
  }, []);

  return (
    <div className="keyboard">
      {rows.map((row, rowIndex) => (
        <div className="key-row" key={rowIndex}>
          {row.map((key, keyIndex) => (
            <span
              key={keyIndex}
              className={`key key-${key.color} ${pressed === key.legend ? "is-pressed" : ""}`}
              aria-hidden="true"
            >
              <span className="key-face">{key.legend}</span>
            </span>
          ))}
          {rowIndex === 1 && (
            <a
              href="#projects"
              className={`key key-cream key-enter ${pressed === "ENTER" ? "is-pressed" : ""}`}
              aria-label="Jump to projects"
            >
              <span className="key-face">Enter</span>
            </a>
          )}
        </div>
      ))}
    </div>
  );
}
