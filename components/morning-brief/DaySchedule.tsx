"use client";

import { useEffect, useState, type FormEvent } from "react";
import type { NewEvent, Owner, ScheduleItem, Suggestion, TravelMode } from "@/lib/morning-brief/types";

export type AddEvent = (event: NewEvent) => Promise<void>;

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
          {item.calendar === "work" ? (item.usual ? "Work (usual hours)" : "Work") : item.title}
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

// A suggested time is one line. Tapping it shows the button that adds it to the calendar.
function SuggestionRow({
  item,
  date,
  open,
  onToggle,
  onAdd,
}: {
  item: Suggestion;
  date: string;
  open: boolean;
  onToggle: () => void;
  onAdd?: AddEvent;
}) {
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState("");

  async function add() {
    if (!onAdd) return;
    setAdding(true);
    setError("");
    try {
      // Once added, the real event takes this row's place.
      await onAdd({ title: item.title, date, start: item.start, end: item.end });
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "It didn't save.");
      setAdding(false);
    }
  }

  return (
    <li className="schedule-item is-suggested">
      <button type="button" className="suggestion-toggle" aria-expanded={open} onClick={onToggle}>
        <span className="schedule-time">
          {formatTime(toMinutes(item.start))}
          <span>{formatTime(toMinutes(item.end))}</span>
        </span>
        <span className="schedule-title">
          <span className="visually-hidden">Suggested: </span>
          {item.title}
        </span>
      </button>
      {open && (
        <button type="button" className="add-button" disabled={!onAdd || adding} onClick={add}>
          {adding ? "Adding…" : "Add"}
        </button>
      )}
      {error && (
        <p className="gate-error suggestion-error" role="alert">
          {error}
        </p>
      )}
    </li>
  );
}

function EventForm({ date, onAdd }: { date: string; onAdd?: AddEvent }) {
  const [title, setTitle] = useState("");
  const [day, setDay] = useState(date);
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [allDay, setAllDay] = useState(false);
  const [status, setStatus] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!onAdd) return;
    setSaving(true);
    setStatus("");
    try {
      await onAdd(allDay ? { title: title.trim(), date: day, allDay: true } : { title: title.trim(), date: day, start, end });
      setStatus(`Added "${title.trim()}" to your Google Calendar.`);
      setTitle("");
    } catch (failure) {
      setStatus(failure instanceof Error ? failure.message : "The event didn't save.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <details className="goal-form">
      <summary>Add an event</summary>
      <form onSubmit={submit}>
        <label>
          Name
          <input type="text" value={title} required maxLength={120} onChange={(event) => setTitle(event.target.value)} />
        </label>
        <label>
          Date
          <input type="date" value={day} required onChange={(event) => setDay(event.target.value)} />
        </label>
        <label className="check-label">
          <input type="checkbox" checked={allDay} onChange={(event) => setAllDay(event.target.checked)} />
          All day
        </label>
        {!allDay && (
          <div className="time-pair">
            <label>
              Starts
              <input type="time" value={start} required onChange={(event) => setStart(event.target.value)} />
            </label>
            <label>
              Ends
              <input type="time" value={end} required onChange={(event) => setEnd(event.target.value)} />
            </label>
          </div>
        )}
        <div className="goal-actions">
          <button type="submit" className="gel-button" disabled={!onAdd || saving}>
            {saving ? "Adding…" : onAdd ? "Add to Google Calendar" : "Add (sample only)"}
          </button>
        </div>
        {status && (
          <p className="muted" role="status">
            {status}
          </p>
        )}
      </form>
    </details>
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

type Entry = { kind: "event"; item: ScheduleItem } | { kind: "suggestion"; item: Suggestion };

export default function DaySchedule({
  items,
  suggestions = [],
  date,
  onAddEvent,
}: {
  items: ScheduleItem[];
  suggestions?: Suggestion[];
  date: string;
  onAddEvent?: AddEvent;
}) {
  const [view, setView] = useState<View>("both");
  const [openSuggestion, setOpenSuggestion] = useState<string | null>(null);
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
  // Suggestions are for his day, so her view leaves them out. All-day events stay on top.
  const rows: Entry[] = [
    ...shown.map((item): Entry => ({ kind: "event", item })),
    ...(view === "hers" ? [] : suggestions.map((item): Entry => ({ kind: "suggestion", item }))),
  ].sort((a, b) => {
    const aAllDay = a.kind === "event" && Boolean(a.item.allDay);
    const bAllDay = b.kind === "event" && Boolean(b.item.allDay);
    if (aAllDay !== bAllDay) return aAllDay ? -1 : 1;
    return a.item.start.localeCompare(b.item.start);
  });

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
      {rows.length === 0 ? (
        <p>Nothing on the calendar today.</p>
      ) : (
        <ol className="schedule">
          {rows.map((row) =>
            row.kind === "event" ? (
              <Row key={`e-${row.item.start}-${row.item.end}-${row.item.title}-${row.item.owner}`} item={row.item} />
            ) : (
              <SuggestionRow
                key={`s-${row.item.start}-${row.item.title}`}
                item={row.item}
                date={date}
                open={openSuggestion === `${row.item.start}-${row.item.title}`}
                onToggle={() => {
                  const key = `${row.item.start}-${row.item.title}`;
                  setOpenSuggestion((current) => (current === key ? null : key));
                }}
                onAdd={onAddEvent}
              />
            ),
          )}
        </ol>
      )}
      <EventForm date={date} onAdd={onAddEvent} />
    </>
  );
}
