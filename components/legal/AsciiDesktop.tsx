"use client";

import { useRef } from "react";
import { useAsciiPile } from "@/lib/useAsciiPile";

export default function AsciiDesktop({ children }: { children: React.ReactNode }) {
  const surfaceRef = useRef<HTMLElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  useAsciiPile(surfaceRef, canvasRef, "a, button, .window");

  return (
    <main className="legal" ref={surfaceRef}>
      <canvas className="ascii-canvas" ref={canvasRef} aria-hidden="true" />
      {children}
    </main>
  );
}
