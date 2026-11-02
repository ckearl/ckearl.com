"use client";

import { type PointerEvent, useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from "react";
import { DESKTOP_WINDOWS, type DesktopWindowId, MINIMIZED_KEY, POSITIONS_KEY } from "@/lib/desktopWindows";

type Offset = { x: number; y: number };

function minimizedIds(): string[] {
  try {
    return JSON.parse(localStorage.getItem(MINIMIZED_KEY) ?? "[]");
  } catch {
    return [];
  }
}

function savedOffsets(): Record<string, Offset> {
  try {
    return JSON.parse(localStorage.getItem(POSITIONS_KEY) ?? "{}");
  } catch {
    return {};
  }
}

// Whichever window was touched last sits on top. The ASCII canvas stays behind all of them.
let topLayer = 1;

export default function DesktopWindow({
  id,
  className = "",
  children,
}: {
  id: DesktopWindowId;
  className?: string;
  children: React.ReactNode;
}) {
  const title = DESKTOP_WINDOWS[id];
  const [minimized, setMinimized] = useState(false);
  const [layer, setLayer] = useState<number>();
  const [dragging, setDragging] = useState(false);
  const windowRef = useRef<HTMLElement>(null);
  const offsetRef = useRef<Offset>({ x: 0, y: 0 });
  const grabRef = useRef<Offset>({ x: 0, y: 0 });
  const bodyId = useId();

  // Keeps the whole window inside the desktop, so it can't be lost off an edge.
  const moveTo = useCallback((next: Offset) => {
    const element = windowRef.current!;
    const box = element.getBoundingClientRect();
    const desktop = element.parentElement!.getBoundingClientRect();
    const fit = (value: number, current: number, start: number, end: number, size: number, limit: number) => {
      const home = start - current;
      return Math.round(Math.max(limit - home, Math.min(value, Math.max(limit, end - size) - home)));
    };
    const placed = {
      x: fit(next.x, offsetRef.current.x, box.left, desktop.right, box.width, desktop.left),
      y: fit(next.y, offsetRef.current.y, box.top, desktop.bottom, box.height, desktop.top),
    };
    offsetRef.current = placed;
    element.style.translate = `${placed.x}px ${placed.y}px`;
  }, []);

  useLayoutEffect(() => {
    // The restore script already drew these, so this only syncs state and refits to the screen.
    const saved = savedOffsets()[id] ?? { x: 0, y: 0 };
    offsetRef.current = saved;
    setMinimized(minimizedIds().includes(id));
    moveTo(saved);
  }, [id, moveTo]);

  useEffect(() => {
    const element = windowRef.current!;
    const observer = new ResizeObserver(() => moveTo(offsetRef.current));
    observer.observe(element);
    observer.observe(element.parentElement!);
    return () => observer.disconnect();
  }, [moveTo]);

  const toggle = () => {
    const others = minimizedIds().filter((saved) => saved !== id);
    const next = minimized ? others : [...others, id];
    localStorage.setItem(MINIMIZED_KEY, JSON.stringify(next));
    document.documentElement.dataset.minimized = next.join(" ");
    setMinimized(!minimized);
  };

  const startDrag = (event: PointerEvent<HTMLDivElement>) => {
    if (event.button !== 0 || (event.target as Element).closest("button")) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    grabRef.current = { x: event.clientX - offsetRef.current.x, y: event.clientY - offsetRef.current.y };
    setDragging(true);
  };

  const drag = (event: PointerEvent<HTMLDivElement>) => {
    if (dragging) moveTo({ x: event.clientX - grabRef.current.x, y: event.clientY - grabRef.current.y });
  };

  const endDrag = () => {
    if (!dragging) return;
    setDragging(false);
    localStorage.setItem(POSITIONS_KEY, JSON.stringify({ ...savedOffsets(), [id]: offsetRef.current }));
  };

  return (
    <section
      ref={windowRef}
      className={`window desktop-window ${className} ${dragging ? "is-dragging" : ""}`}
      data-window={id}
      style={{ translate: `var(--window-${id}, 0px 0px)`, zIndex: layer }}
      aria-label={title}
      onPointerDownCapture={() => setLayer(++topLayer)}
    >
      <div
        className="window-title"
        onPointerDown={startDrag}
        onPointerMove={drag}
        onPointerUp={endDrag}
        onPointerCancel={endDrag}
      >
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
