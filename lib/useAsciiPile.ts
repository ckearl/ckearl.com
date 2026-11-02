import { type RefObject, useCallback, useEffect, useRef, useState } from "react";
import { AsciiPile } from "@/lib/asciiPile";

// Distance between characters along a drag, in pixels.
const TRAIL_SPACING = 7;
const MAX_TRAIL = 24;
const SPREAD = 10;

// Drops ASCII where the pointer drags on a surface. Presses that start on `ignore` are left alone.
export function useAsciiPile(
  surfaceRef: RefObject<HTMLElement | null>,
  canvasRef: RefObject<HTMLCanvasElement | null>,
  ignore: string
) {
  const pileRef = useRef<AsciiPile | null>(null);
  const [hasPile, setHasPile] = useState(false);

  useEffect(() => {
    const surface = surfaceRef.current!;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const pile = new AsciiPile(canvasRef.current!, reduceMotion, setHasPile);
    pileRef.current = pile;

    let frame = 0;
    let lastTime = 0;
    let held = false;
    let pointer = { x: 0, y: 0 };

    // Pointer positions stay in viewport coordinates, because the surface moves
    // under a finger while the page scrolls.
    const spawnAt = (x: number, y: number) => {
      const bounds = surface.getBoundingClientRect();
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
      target instanceof Element && target.closest(ignore) !== null;

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
      pile.resize(surface.clientWidth, surface.clientHeight);
    });
    observer.observe(surface);

    surface.addEventListener("pointerdown", onPointerDown);
    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", release);
    window.addEventListener("pointercancel", release);
    surface.addEventListener("touchstart", onTouchStart, { passive: true });
    surface.addEventListener("touchmove", onTouchMove, { passive: true });
    surface.addEventListener("touchend", release);
    surface.addEventListener("touchcancel", release);

    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
      surface.removeEventListener("pointerdown", onPointerDown);
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", release);
      window.removeEventListener("pointercancel", release);
      surface.removeEventListener("touchstart", onTouchStart);
      surface.removeEventListener("touchmove", onTouchMove);
      surface.removeEventListener("touchend", release);
      surface.removeEventListener("touchcancel", release);
    };
  }, [surfaceRef, canvasRef, ignore]);

  const clear = useCallback(() => pileRef.current?.clear(), []);

  return { hasPile, clear };
}
