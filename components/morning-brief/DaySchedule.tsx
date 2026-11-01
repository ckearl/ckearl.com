"use client";

import { useState } from "react";
import type { ScheduleItem, TravelMode } from "@/lib/morning-brief/types";

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
    <li className={`schedule-item is-${item.calendar}`}>
      <p className="schedule-time">
        {formatTime(toMinutes(item.start))}
        <span>{formatTime(toMinutes(item.end))}</span>
      </p>
      <div>
        <p className="schedule-title">
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

export default function DaySchedule({ items }: { items: ScheduleItem[] }) {
  return (
    <ol className="schedule">
      {items.map((item) => (
        <Row key={item.start} item={item} />
      ))}
    </ol>
  );
}
