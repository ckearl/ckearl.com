"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import BriefView from "@/components/morning-brief/BriefView";
import Window from "@/components/new-design/Window";
import { sampleBrief } from "@/data/morning-brief/sample";
import type { Brief, GoalRequest, MealDay, MealsRequest, NewEvent, ScheduleItem, Training } from "@/lib/morning-brief/types";

const API_URL = process.env.NEXT_PUBLIC_BRIEF_API;
const TOKEN_KEY = "morning-brief-token";
const OLD_PASSWORD_KEY = "morning-brief-password";

type State = "checking" | "locked" | "ready";

function denverToday() {
  return new Date().toLocaleDateString("en-CA", { timeZone: "America/Denver" });
}

export default function BriefGate() {
  const [state, setState] = useState<State>(API_URL ? "checking" : "ready");
  const [brief, setBrief] = useState<Brief | null>(API_URL ? null : sampleBrief);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const load = useCallback(async (token: string) => {
    const response = await fetch(`${API_URL}/brief/today`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    if (response.status === 401) {
      localStorage.removeItem(TOKEN_KEY);
      setState("locked");
      return;
    }
    if (!response.ok) throw new Error(String(response.status));
    setBrief(await response.json());
    setState("ready");
  }, []);

  const showLoadError = useCallback(() => {
    setError("The brief didn't load. Check your connection and try again.");
    setState("locked");
  }, []);

  const logIn = async (attempt: string) => {
    setError("");
    try {
      const response = await fetch(`${API_URL}/brief/session`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: attempt }),
      });
      if (response.status === 401) {
        setError("That password didn't work.");
        return;
      }
      if (!response.ok) throw new Error(String(response.status));
      const { token } = await response.json();
      localStorage.setItem(TOKEN_KEY, token);
      await load(token);
    } catch {
      showLoadError();
    }
  };

  useEffect(() => {
    if (!API_URL) return;
    localStorage.removeItem(OLD_PASSWORD_KEY);
    const saved = localStorage.getItem(TOKEN_KEY);
    if (saved) load(saved).catch(showLoadError);
    else setState("locked");
  }, [load, showLoadError]);

  // Sends a change from the page and returns the reply, or throws with the backend's message.
  async function post<T>(path: string, body: unknown, failure: string): Promise<T> {
    const token = localStorage.getItem(TOKEN_KEY);
    const response = await fetch(`${API_URL}${path}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.error ?? failure);
    return result as T;
  }

  // Saves the event to train for. The backend replans today's Training section and sends it back.
  const saveGoal = async (goal: GoalRequest) => {
    const result = await post<{ training?: Training }>("/brief/goal", goal, "The goal didn't save.");
    if (result.training) setBrief((current) => current && { ...current, training: result.training });
    return Boolean(result.training);
  };

  const saveMeals = async (meals: MealsRequest) => {
    const result = await post<{ meals: MealDay[] }>("/brief/meals", meals, "The meals didn't save.");
    setBrief((current) => current && { ...current, meals: result.meals });
  };

  // Adds to Google Calendar. An event for today joins the schedule and replaces the suggestion it came from.
  const addEvent = async (event: NewEvent) => {
    const result = await post<{ item: ScheduleItem | null }>("/brief/event", event, "The event didn't save.");
    const item = result.item;
    if (!item) return;
    setBrief(
      (current) =>
        current && {
          ...current,
          schedule: [...(current.schedule ?? []), item],
          suggestions: current.suggestions?.filter(
            (suggestion) => !(suggestion.title === item.title && suggestion.start === item.start),
          ),
        },
    );
  };

  if (state === "ready" && brief) {
    return (
      <BriefView
        brief={brief}
        stale={!brief.sample && brief.date !== denverToday()}
        onSaveGoal={API_URL ? saveGoal : undefined}
        onSaveMeals={API_URL ? saveMeals : undefined}
        onAddEvent={API_URL ? addEvent : undefined}
      />
    );
  }

  const submit = (event: FormEvent) => {
    event.preventDefault();
    logIn(password);
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
