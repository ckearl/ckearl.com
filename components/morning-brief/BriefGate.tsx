"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import BriefView from "@/components/morning-brief/BriefView";
import Window from "@/components/new-design/Window";
import { sampleBrief } from "@/data/morning-brief/sample";
import type { Brief } from "@/lib/morning-brief/types";

const API_URL = process.env.NEXT_PUBLIC_BRIEF_API;
const PASSWORD_KEY = "morning-brief-password";

type State = "checking" | "locked" | "ready";

function denverToday() {
  return new Date().toLocaleDateString("en-CA", { timeZone: "America/Denver" });
}

export default function BriefGate() {
  const [state, setState] = useState<State>(API_URL ? "checking" : "ready");
  const [brief, setBrief] = useState<Brief | null>(API_URL ? null : sampleBrief);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const open = useCallback(async (attempt: string) => {
    setError("");
    try {
      const response = await fetch(`${API_URL}/brief/today`, {
        headers: { "X-Brief-Password": attempt },
        cache: "no-store",
      });
      if (response.status === 401) {
        const wasSaved = attempt === localStorage.getItem(PASSWORD_KEY);
        localStorage.removeItem(PASSWORD_KEY);
        setError(wasSaved ? "" : "That password didn't work.");
        setState("locked");
        return;
      }
      if (!response.ok) throw new Error(String(response.status));
      setBrief(await response.json());
      localStorage.setItem(PASSWORD_KEY, attempt);
      setState("ready");
    } catch {
      setError("The brief didn't load. Check your connection and try again.");
      setState("locked");
    }
  }, []);

  useEffect(() => {
    if (!API_URL) return;
    const saved = localStorage.getItem(PASSWORD_KEY);
    if (saved) open(saved);
    else setState("locked");
  }, [open]);

  if (state === "ready" && brief) {
    return <BriefView brief={brief} stale={!brief.sample && brief.date !== denverToday()} />;
  }

  const submit = (event: FormEvent) => {
    event.preventDefault();
    open(password);
  };

  return (
    <main className="gate">
      <Window title="Morning Brief" className="brief-window">
        {state === "checking" ? (
          <p>Loading today&apos;s brief.</p>
        ) : (
          <form onSubmit={submit}>
            <label>
              Password
              <input
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </label>
            {error && <p className="gate-error">{error}</p>}
            <button type="submit" className="gel-button">Open brief</button>
          </form>
        )}
      </Window>
    </main>
  );
}
