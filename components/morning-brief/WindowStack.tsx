"use client";

import { useEffect, useLayoutEffect, useRef, useState, type PointerEvent as ReactPointerEvent, type ReactNode } from "react";
import BriefWindow from "@/components/morning-brief/BriefWindow";

export type Pane = { id: string; title: string; content: ReactNode };

const ORDER_KEY = "morning-brief-order";
// How far the pointer moves before a press on a title bar becomes a drag.
const DRAG_DISTANCE = 6;
// Near the top or bottom of the screen, the page scrolls while dragging.
const EDGE = 64;
const SCROLL_STEP = 14;

function savedOrder(): string[] {
  try {
    const saved = JSON.parse(localStorage.getItem(ORDER_KEY) ?? "[]");
    return Array.isArray(saved) ? saved : [];
  } catch {
    return [];
  }
}

function saveOrder(order: string[]) {
  try {
    localStorage.setItem(ORDER_KEY, JSON.stringify(order));
  } catch {
    // The order just won't be remembered.
  }
}

// The saved order, with any window it doesn't know yet at its usual place.
export function arrange(ids: string[], saved: string[]): string[] {
  const order = saved.filter((id) => ids.includes(id));
  ids.forEach((id, index) => {
    if (!order.includes(id)) order.splice(Math.min(index, order.length), 0, id);
  });
  return order;
}

function moveTo(order: string[], id: string, target: string, after: boolean): string[] {
  const rest = order.filter((other) => other !== id);
  const index = rest.indexOf(target) + (after ? 1 : 0);
  return [...rest.slice(0, index), id, ...rest.slice(index)];
}

type Drag = {
  id: string;
  pointerId: number;
  startX: number;
  startY: number;
  startScroll: number;
  moving: boolean;
  drop?: { target: string; after: boolean };
};

// The brief's windows in the order chosen on this device. A window moves by dragging its title
// bar, or with the arrow keys on its focused title.
export default function WindowStack({ panes }: { panes: Pane[] }) {
  const ids = panes.map((pane) => pane.id);
  const [saved, setSaved] = useState<string[]>([]);
  const [drag, setDrag] = useState<Drag | null>(null);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const dragRef = useRef<Drag | null>(null);
  const pointer = useRef({ x: 0, y: 0 });
  const nodes = useRef(new Map<string, HTMLElement>());

  useLayoutEffect(() => setSaved(savedOrder()), []);

  const order = arrange(ids, saved);

  function commit(next: string[]) {
    setSaved(next);
    saveOrder(next);
  }

  function update(next: Drag | null) {
    dragRef.current = next;
    setDrag(next);
  }

  function place() {
    const current = dragRef.current;
    if (!current) return;
    const { x, y } = pointer.current;
    setOffset({ x: x - current.startX, y: y - current.startY + (window.scrollY - current.startScroll) });
    let drop: Drag["drop"];
    for (const [id, node] of nodes.current) {
      if (id === current.id) continue;
      const box = node.getBoundingClientRect();
      if (x >= box.left && x <= box.right && y >= box.top && y <= box.bottom) {
        drop = { target: id, after: y > box.top + box.height / 2 };
      }
    }
    if (drop?.target !== current.drop?.target || drop?.after !== current.drop?.after) update({ ...current, drop });
  }

  // Scrolls near the screen's edges so a window can travel the whole page.
  useEffect(() => {
    if (!drag?.moving) return;
    let frame = requestAnimationFrame(function step() {
      const { y } = pointer.current;
      const delta = y < EDGE ? -SCROLL_STEP : y > window.innerHeight - EDGE ? SCROLL_STEP : 0;
      if (delta) {
        window.scrollBy(0, delta);
        place();
      }
      frame = requestAnimationFrame(step);
    });
    return () => cancelAnimationFrame(frame);
    // place reads refs only, so the loop restarts just when a drag starts or ends.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [drag?.moving]);

  function down(event: ReactPointerEvent, id: string) {
    const target = event.target as HTMLElement;
    if (!target.closest(".window-title") || target.closest("button") || event.button !== 0) return;
    pointer.current = { x: event.clientX, y: event.clientY };
    update({ id, pointerId: event.pointerId, startX: event.clientX, startY: event.clientY, startScroll: window.scrollY, moving: false });
  }

  function move(event: ReactPointerEvent) {
    const current = dragRef.current;
    if (!current || event.pointerId !== current.pointerId) return;
    pointer.current = { x: event.clientX, y: event.clientY };
    if (!current.moving) {
      if (Math.hypot(event.clientX - current.startX, event.clientY - current.startY) < DRAG_DISTANCE) return;
      try {
        (event.currentTarget as HTMLElement).setPointerCapture(event.pointerId);
      } catch {
        // Without capture the drag still follows moves over this window.
      }
      update({ ...current, moving: true });
    }
    place();
  }

  function up(event: ReactPointerEvent) {
    const current = dragRef.current;
    if (!current || event.pointerId !== current.pointerId) return;
    if (current.moving && current.drop) commit(moveTo(order, current.id, current.drop.target, current.drop.after));
    update(null);
    setOffset({ x: 0, y: 0 });
  }

  function step(id: string, by: -1 | 1) {
    const index = order.indexOf(id);
    const target = order[index + by];
    if (!target) return;
    commit(moveTo(order, id, target, by === 1));
    requestAnimationFrame(() => nodes.current.get(id)?.querySelector<HTMLElement>(".window-title h2")?.focus());
  }

  const byId = new Map(panes.map((pane) => [pane.id, pane]));
  return (
    <>
      {order.map((id) => {
        const pane = byId.get(id)!;
        const dragging = drag?.moving && drag.id === id;
        const drop = drag?.moving && drag.drop?.target === id ? (drag.drop.after ? "drop-after" : "drop-before") : "";
        return (
          <div
            key={id}
            ref={(node) => {
              if (node) nodes.current.set(id, node);
              else nodes.current.delete(id);
            }}
            className={`window-slot ${dragging ? "is-dragging" : ""} ${drop}`}
            style={dragging ? { transform: `translate(${offset.x}px, ${offset.y}px)` } : undefined}
            onPointerDown={(event) => down(event, id)}
            onPointerMove={move}
            onPointerUp={up}
            onPointerCancel={up}
          >
            <BriefWindow title={pane.title} onMove={(by) => step(id, by)}>
              {pane.content}
            </BriefWindow>
          </div>
        );
      })}
    </>
  );
}
