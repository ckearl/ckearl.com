"use client";

import { useState, type FormEvent } from "react";
import type { MealDay, MealsRequest } from "@/lib/morning-brief/types";

export type SaveMeals = (meals: MealsRequest) => Promise<void>;

function MealsForm({ meals, onSave }: { meals: MealDay[]; onSave?: SaveMeals }) {
  const [days, setDays] = useState(() =>
    Object.fromEntries(meals.map((day) => [day.date, { lunch: day.lunch ?? "", dinner: day.dinner ?? "" }])),
  );
  const [status, setStatus] = useState("");
  const [saving, setSaving] = useState(false);

  function change(date: string, meal: "lunch" | "dinner", value: string) {
    setDays((current) => ({ ...current, [date]: { ...current[date], [meal]: value } }));
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!onSave) return;
    setSaving(true);
    setStatus("");
    try {
      await onSave({ days });
      setStatus("Saved. Tomorrow's brief plans shopping and prep around these.");
    } catch (failure) {
      setStatus(failure instanceof Error ? failure.message : "The meals didn't save.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <details className="goal-form">
      <summary>Write the week&apos;s meals</summary>
      <form onSubmit={submit}>
        {meals.map((day) => (
          <fieldset key={day.date} className="meal-day">
            <legend>{day.day}</legend>
            <label>
              Lunch
              <input
                type="text"
                value={days[day.date].lunch}
                maxLength={120}
                onChange={(event) => change(day.date, "lunch", event.target.value)}
              />
            </label>
            <label>
              Dinner
              <input
                type="text"
                value={days[day.date].dinner}
                maxLength={120}
                onChange={(event) => change(day.date, "dinner", event.target.value)}
              />
            </label>
          </fieldset>
        ))}
        <div className="goal-actions">
          <button type="submit" className="gel-button" disabled={!onSave || saving}>
            {saving ? "Saving…" : onSave ? "Save meals" : "Save (sample only)"}
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

export default function MealPlan({ meals, onSave }: { meals: MealDay[]; onSave?: SaveMeals }) {
  const written = meals.some((day) => day.lunch || day.dinner);
  return (
    <>
      {written ? (
        <ol className="week-plan meal-list">
          {meals.map((day, index) => (
            <li key={day.date} className={index === 0 ? "is-today" : undefined} aria-current={index === 0 ? "date" : undefined}>
              <span>{day.day}</span>
              <div>
                {day.lunch && <p>Lunch: {day.lunch}</p>}
                {day.dinner && <p>Dinner: {day.dinner}</p>}
                {!day.lunch && !day.dinner && <p className="muted">Nothing planned</p>}
              </div>
            </li>
          ))}
        </ol>
      ) : (
        <p>No meals written for the coming week yet.</p>
      )}
      <MealsForm key={JSON.stringify(meals)} meals={meals} onSave={onSave} />
    </>
  );
}
