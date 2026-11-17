"use client";

import { useState, type FormEvent } from "react";
import type { DoneRequest, GoalKind, GoalRequest, Training, Workout } from "@/lib/morning-brief/types";

export type MarkDone = (mark: DoneRequest) => Promise<void>;

const KINDS: { kind: GoalKind; label: string }[] = [
  { kind: "5k", label: "5K" },
  { kind: "10k", label: "10K" },
  { kind: "half", label: "Half marathon" },
  { kind: "marathon", label: "Marathon" },
  { kind: "swim", label: "Swim event" },
];

type SaveGoal = (goal: GoalRequest) => Promise<boolean>;

function GoalForm({ training, onSave }: { training: Training; onSave?: SaveGoal }) {
  const goal = training.goal;
  const [name, setName] = useState(goal?.name ?? "");
  const [kind, setKind] = useState<GoalKind>(goal?.kind ?? "half");
  const [date, setDate] = useState(goal?.date ?? "");
  const [status, setStatus] = useState("");
  const [saving, setSaving] = useState(false);

  async function save(request: GoalRequest) {
    if (!onSave) return;
    setSaving(true);
    setStatus("");
    try {
      const replanned = await onSave(request);
      setStatus(replanned ? "Saved. The plan above is updated." : "Saved. Tomorrow's brief will plan around it.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "The goal didn't save.");
    } finally {
      setSaving(false);
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    save({ name: name.trim(), kind, date });
  }

  return (
    <details className="goal-form">
      <summary>{goal ? "Change the event" : "Add an event to train for"}</summary>
      <form onSubmit={submit}>
        <label>
          Event name
          <input type="text" value={name} maxLength={80} placeholder="St. George Half" onChange={(event) => setName(event.target.value)} />
        </label>
        <label>
          Distance
          <select value={kind} onChange={(event) => setKind(event.target.value as GoalKind)}>
            {KINDS.map((option) => (
              <option key={option.kind} value={option.kind}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Event date
          <input type="date" value={date} required onChange={(event) => setDate(event.target.value)} />
        </label>
        <div className="goal-actions">
          <button type="submit" className="gel-button" disabled={!onSave || saving}>
            {saving ? "Saving…" : onSave ? "Save and replan" : "Save (sample only)"}
          </button>
          {goal && (
            <button type="button" className="text-button" disabled={!onSave || saving} onClick={() => save({ clear: true })}>
              Back to general fitness
            </button>
          )}
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

// One line per workout. Tapping the name opens the suggested workout; the box checks it off.
function WorkoutLine({ item, date, onMark }: { item: Workout; date: string; onMark?: MarkDone }) {
  const [done, setDone] = useState(Boolean(item.done));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function toggle(next: boolean) {
    if (!onMark || !item.kind) return;
    setDone(next);
    setSaving(true);
    setError("");
    try {
      await onMark({ date, kind: item.kind, done: next });
    } catch (failure) {
      setDone(!next);
      setError(failure instanceof Error ? failure.message : "That didn't save.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <li className={done ? "is-done" : undefined}>
      {item.kind && (
        <input
          type="checkbox"
          checked={done}
          disabled={!onMark || saving}
          aria-label={`Done: ${item.title}`}
          onChange={(event) => toggle(event.target.checked)}
        />
      )}
      <details className="expander">
        <summary>{item.title}</summary>
        <p>{item.detail}</p>
      </details>
      {error && (
        <p className="gate-error" role="alert">
          {error}
        </p>
      )}
    </li>
  );
}

export default function TrainingPlan({
  training,
  date,
  onSaveGoal,
  onMarkDone,
}: {
  training: Training;
  date: string;
  onSaveGoal?: SaveGoal;
  onMarkDone?: MarkDone;
}) {
  return (
    <>
      <ul className="workout-list">
        {training.today.map((item) => (
          <WorkoutLine key={`${item.title}-${item.done}`} item={item} date={date} onMark={onMarkDone} />
        ))}
      </ul>
      {training.gymNext && <p className="gym-next">{training.gymNext}</p>}
      <details className="expander">
        <summary>This week</summary>
        <p className="muted">Focus: {training.focus}</p>
        <p>{training.why}</p>
        {training.plan && (
          <ol className="week-plan">
            {training.plan.map((day) => (
              <li key={day.date} className={day.today ? "is-today" : undefined} aria-current={day.today ? "date" : undefined}>
                <span>{day.day}</span>
                {day.items.join(", ")}
              </li>
            ))}
          </ol>
        )}
        <h3>Done so far</h3>
        <dl className="week-meters">
          {training.week.map((item) => (
            <div key={item.label}>
              <dt>{item.label}</dt>
              <dd>
                {item.done} of {item.target}
              </dd>
              <span className="bar" aria-hidden="true">
                <span style={{ width: `${Math.min(100, (item.done / item.target) * 100)}%` }} />
              </span>
            </div>
          ))}
        </dl>
      </details>
      <GoalForm key={training.goal ? JSON.stringify(training.goal) : "none"} training={training} onSave={onSaveGoal} />
    </>
  );
}
