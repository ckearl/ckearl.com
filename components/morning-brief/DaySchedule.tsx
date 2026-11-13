"use client";

import { useEffect, useState } from "react";
import type { Owner, ScheduleItem, TravelMode } from "@/lib/morning-brief/types";

type View = "both" | "mine" | "hers";

const VIEWS: { view: View; label: string }[] = [
  { view: "both", label: "Both" },
  { view: "mine", label: "Mine" },
  { view: "hers", label: "Hers" },
];

const VIEW_KEY = "morning-brief-calendar-view";

// Shared events show in either person's view.
const SHOWN: Record<View, Owner[]> = {
  both: ["mine", "hers", "shared"],
  mine: ["mine", "shared"],
  hers: ["hers", "shared"],
};

const OWNER_LABELS: Record<Owner, string> = { mine: "Mine", hers: "Hers", shared: "Shared" };

const MODES: { mode: TravelMode; label: string }[] = [
  { mode: "walk", label: "Walk" },
  { mode: "bike", label: "Bike" },
  { mode: "drive", label: "Drive" },
];

// Time to park, lock up or walk in.
const BUFFER_MINUTES = 5;

function toMinutes(time: string) {
  const [hours, minutes] = time.split(":").map(Number);
  return hours * 60 + minutes;
}

function formatTime(total: number) {
  const hours = Math.floor(total / 60);
  const minutes = String(total % 60).padStart(2, "0");
  return `${hours % 12 || 12}:${minutes} ${hours < 12 ? "AM" : "PM"}`;
}

function Row({ item }: { item: ScheduleItem }) {
  const [mode, setMode] = useState(item.travel?.mode);
  const minutes = item.travel && mode ? item.travel.minutes[mode] : 0;
  const leaveBy = toMinutes(item.start) - minutes - BUFFER_MINUTES;

  return (
    <li className={`schedule-item is-${item.calendar} owner-${item.owner ?? "mine"}`}>
      <p className="schedule-time">
        {item.allDay ? (
          "All day"
        ) : (
          <>
            {formatTime(toMinutes(item.start))}
            <span>{formatTime(toMinutes(item.end))}</span>
          </>
        )}
      </p>
      <div>
        <p className="schedule-title">
          <span className="visually-hidden">{OWNER_LABELS[item.owner ?? "mine"]}: </span>
          {item.calendar === "work" ? "Work" : item.title}
          {item.place && <span> in {item.place}</span>}
        </p>
        {item.travel && mode && (
          <>
            <p className="schedule-leave">
              Leave by <strong>{formatTime(leaveBy)}</strong>
            </p>
            <div className="mode-picker" role="group" aria-label={`Travel to ${item.title}`}>
              {MODES.map((option) => (
                <button
                  key={option.mode}
                  type="button"
                  aria-pressed={option.mode === mode}
                  onClick={() => setMode(option.mode)}
                >
                  <span>{option.label}</span>
                  {item.travel!.minutes[option.mode]} min
                </button>
              ))}
            </div>
          </>
        )}
      </div>
    </li>
  );
}

function savedView(): View {
  try {
    const saved = window.localStorage.getItem(VIEW_KEY);
    return saved === "mine" || saved === "hers" ? saved : "both";
  } catch {
    return "both";
  }
}

export default function DaySchedule({ items }: { items: ScheduleItem[] }) {
  const [view, setView] = useState<View>("both");
  useEffect(() => setView(savedView()), []);

  function choose(next: View) {
    setView(next);
    try {
      window.localStorage.setItem(VIEW_KEY, next);
    } catch {
      // The choice just won't be remembered.
    }
  }

  const hasHers = items.some((item) => item.owner === "hers");
  const shown = hasHers ? items.filter((item) => SHOWN[view].includes(item.owner ?? "mine")) : items;

  return (
    <>
      {hasHers && (
        <div className="mode-picker calendar-picker" role="group" aria-label="Whose calendar">
          {VIEWS.map((option) => (
            <button key={option.view} type="button" aria-pressed={option.view === view} onClick={() => choose(option.view)}>
              {option.view !== "both" && <i className={`owner-swatch owner-${option.view}`} aria-hidden="true" />}
              {option.label}
            </button>
          ))}
        </div>
      )}
      {shown.length === 0 ? (
        <p>Nothing on the calendar today.</p>
      ) : (
        <ol className="schedule">
          {shown.map((item) => (
            <Row key={`${item.start}-${item.end}-${item.title}-${item.owner}`} item={item} />
          ))}
        </ol>
      )}
    </>
  );
}
