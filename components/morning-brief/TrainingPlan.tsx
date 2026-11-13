"use client";

import { useState, type FormEvent } from "react";
import type { GoalKind, GoalRequest, Training } from "@/lib/morning-brief/types";

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

export default function TrainingPlan({ training, onSaveGoal }: { training: Training; onSaveGoal?: SaveGoal }) {
  return (
    <>
      <p className="muted">Focus: {training.focus}</p>
      <ul className="plan-list">
        {training.today.map((item) => (
          <li key={item.title}>
            <p>
              <strong>{item.title}</strong>
            </p>
            <p>{item.detail}</p>
          </li>
        ))}
      </ul>
      <p>{training.why}</p>
      {training.plan && (
        <>
          <h3>The week</h3>
          <ol className="week-plan">
            {training.plan.map((day) => (
              <li key={day.date} className={day.today ? "is-today" : undefined} aria-current={day.today ? "date" : undefined}>
                <span>{day.day}</span>
                {day.items.join(", ")}
              </li>
            ))}
          </ol>
        </>
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
      <GoalForm key={training.goal ? JSON.stringify(training.goal) : "none"} training={training} onSave={onSaveGoal} />
      <p className="muted fine-print">A plan from simple rules, not coaching or medical advice. Ease off if something hurts.</p>
    </>
  );
}
