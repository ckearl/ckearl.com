"use client";

import { useEffect, useState, type FormEvent } from "react";
import type {
  NewEvent,
  Owner,
  Replan,
  ScheduleItem,
  Suggestion,
  SuggestionMark,
  SuggestionOutcome,
  TravelMode,
} from "@/lib/morning-brief/types";

export type AddEvent = (event: NewEvent) => Promise<void>;
export type MarkSuggestion = (mark: SuggestionMark) => Promise<void>;
export type ReplanDay = () => Promise<void>;

// Matches the backend: a replan still "running" after this long has failed.
const REPLAN_LIMIT_MS = 4 * 60 * 1000;

type View = "both" | "mine" | "hers";

const VIEWS: { view: View; label: string }[] = [
  { view: "both", label: "Both" },
  { view: "mine", label: "Mine" },
  { view: "hers", label: "Hers" },
];

const VIEW_KEY = "morning-brief-calendar-view";
const SUGGESTIONS_KEY = "morning-brief-show-suggestions";

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

const OUTCOME_LABELS: Record<SuggestionOutcome, string> = { done: "Done", skipped: "Skipped" };

// A suggested time is one line. Tapping it shows buttons to add it to the calendar, or to mark it
// done or skipped, which shapes later plans. A marked one can be taken back.
function SuggestionRow({
  item,
  date,
  open,
  onToggle,
  onAdd,
  onMark,
}: {
  item: Suggestion;
  date: string;
  open: boolean;
  onToggle: () => void;
  onAdd?: AddEvent;
  onMark?: MarkSuggestion;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function run(action: () => Promise<void>) {
    setBusy(true);
    setError("");
    try {
      await action();
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "It didn't save.");
    } finally {
      setBusy(false);
    }
  }

  // Once added, the real event takes this row's place.
  const add = () => run(() => onAdd!({ title: item.title, date, start: item.start, end: item.end }));
  const mark = (outcome: SuggestionMark["outcome"]) =>
    run(() => onMark!({ date, kind: item.kind, title: item.title, start: item.start, outcome }));

  return (
    <li className={`schedule-item is-suggested ${item.outcome ? `is-${item.outcome}` : ""}`}>
      <button type="button" className="suggestion-toggle" aria-expanded={open} onClick={onToggle}>
        <span className="schedule-time">
          {formatTime(toMinutes(item.start))}
          <span>{formatTime(toMinutes(item.end))}</span>
        </span>
        <span className="schedule-title">
          <span className="visually-hidden">Suggested: </span>
          {item.title}
          {item.outcome && <span className="suggestion-outcome">{OUTCOME_LABELS[item.outcome]}</span>}
        </span>
      </button>
      {open && (
        <div className="suggestion-actions">
          {item.outcome ? (
            <button type="button" disabled={!onMark || busy} onClick={() => mark("clear")}>
              Undo
            </button>
          ) : (
            <>
              <button type="button" className="is-primary" disabled={!onAdd || busy} onClick={add}>
                Add
              </button>
              <button type="button" disabled={!onMark || busy} onClick={() => mark("done")}>
                Done
              </button>
              <button type="button" disabled={!onMark || busy} onClick={() => mark("skipped")}>
                Skip
              </button>
            </>
          )}
        </div>
      )}
      {error && (
        <p className="gate-error suggestion-error" role="alert">
          {error}
        </p>
      )}
    </li>
  );
}

// Redoes the rest of today's suggestions around the calendar as it is now. It runs in the
// background, so the page shows that it's working until the new plan arrives.
function ReplanButton({ replan, onReplan }: { replan?: Replan; onReplan?: ReplanDay }) {
  const [error, setError] = useState("");
  const [starting, setStarting] = useState(false);
  const running = replan?.state === "running" && Date.now() - Date.parse(replan.at) < REPLAN_LIMIT_MS;

  async function start() {
    if (!onReplan) return;
    setStarting(true);
    setError("");
    try {
      await onReplan();
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "The replan didn't start.");
    } finally {
      setStarting(false);
    }
  }

  return (
    <>
      <button type="button" className="text-button replan-button" disabled={!onReplan || running || starting} onClick={start}>
        {running || starting ? "Replanning…" : "Replan from now"}
      </button>
      <span className="replan-status" role="status">
        {running ? "About a minute." : replan?.state === "failed" ? "The last replan didn't finish. Try again." : ""}
      </span>
      {error && (
        <p className="gate-error" role="alert">
          {error}
        </p>
      )}
    </>
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

function savedShowSuggestions(): boolean {
  try {
    return window.localStorage.getItem(SUGGESTIONS_KEY) !== "off";
  } catch {
    return true;
  }
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
  replan,
  onAddEvent,
  onMarkSuggestion,
  onReplan,
}: {
  items: ScheduleItem[];
  suggestions?: Suggestion[];
  date: string;
  replan?: Replan;
  onAddEvent?: AddEvent;
  onMarkSuggestion?: MarkSuggestion;
  onReplan?: ReplanDay;
}) {
  const [view, setView] = useState<View>("both");
  const [openSuggestion, setOpenSuggestion] = useState<string | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(true);
  useEffect(() => {
    setView(savedView());
    setShowSuggestions(savedShowSuggestions());
  }, []);

  function toggleSuggestions(next: boolean) {
    setShowSuggestions(next);
    try {
      window.localStorage.setItem(SUGGESTIONS_KEY, next ? "on" : "off");
    } catch {
      // The choice just won't be remembered.
    }
  }

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
    ...(view === "hers" || !showSuggestions ? [] : suggestions.map((item): Entry => ({ kind: "suggestion", item }))),
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
      {view !== "hers" && (
        <div className="suggestion-controls">
          {suggestions.length > 0 && (
            <label className="suggestions-switch">
              <input
                type="checkbox"
                role="switch"
                checked={showSuggestions}
                onChange={(event) => toggleSuggestions(event.target.checked)}
              />
              Suggested times
            </label>
          )}
          <ReplanButton replan={replan} onReplan={onReplan} />
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
                onMark={onMarkSuggestion}
              />
            ),
          )}
        </ol>
      )}
      <EventForm date={date} onAdd={onAddEvent} />
    </>
  );
}
