"use client";

import { useEffect, useState } from "react";

const links = [
  { label: "Projects", href: "#projects" },
  { label: "Experience", href: "#experience" },
  { label: "About", href: "#about" },
  { label: "Contact", href: "#contact" },
];

function currentTime() {
  return new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

export default function MenuBar() {
  const [time, setTime] = useState<string | null>(null);

  useEffect(() => {
    setTime(currentTime());
    const timer = setInterval(() => setTime(currentTime()), 10_000);
    return () => clearInterval(timer);
  }, []);

  return (
    <nav className="menu-bar" aria-label="Main">
      <a href="#top" className="menu-mark">
        ck
      </a>
      {links.map((link) => (
        <a key={link.href} href={link.href}>
          {link.label}
        </a>
      ))}
      {time && <time className="menu-clock">{time}</time>}
    </nav>
  );
}
