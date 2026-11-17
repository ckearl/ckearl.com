// The daily brief as stored JSON. The page only renders this shape, and any
// section can be missing on a day it has nothing to say.

export type Team = { abbr: string; name: string; bg: string; fg: string };

export type League = "nba" | "epl" | "laliga" | "seriea" | "bundesliga" | "ligue1" | "nfl" | "nhl" | "mlb";

export type Score = {
  home: { abbr: string; name: string; score: number };
  away: { abbr: string; name: string; score: number };
  status: string;
  url?: string | null; // ESPN Gamecast
};

export type Owner = "mine" | "hers" | "shared";

export type TravelMode = "walk" | "bike" | "drive";

export type ScheduleItem = {
  start: string; // 24-hour "HH:MM"
  end: string;
  title: string;
  calendar: "personal" | "work" | "routine"; // routine is a daily block such as the morning help
  owner?: Owner; // missing on briefs from before owners were tracked, which count as mine
  allDay?: boolean;
  usual?: boolean; // work blocks from the usual work hours, not real meeting times
  place?: string;
  travel?: { minutes: Record<TravelMode, number>; mode: TravelMode };
};

export type TrainingWindow = {
  label: string;
  time: string;
  conditions: string;
  best?: boolean;
  start?: string; // "HH:MM", missing on older briefs
  end?: string;
};

export type SuggestionKind = "todo" | "workout" | "music" | "dinner" | "chores" | "reading" | "groceries" | "meal_prep";

export type SuggestionOutcome = "done" | "skipped";

// A time Claude suggests for something, checked against the calendar so it never overlaps an event.
export type Suggestion = {
  start: string;
  end: string;
  title: string;
  kind: SuggestionKind;
  why?: string; // only on older briefs
  outcome?: SuggestionOutcome; // marked on the page
};

// What marking a suggestion sends. "clear" takes the mark back.
export type SuggestionMark = {
  date: string;
  kind: SuggestionKind;
  title: string;
  start: string;
  outcome: SuggestionOutcome | "clear";
};

// A replan of the rest of the day, run in the background after the button is pressed.
export type Replan = { state: "running" | "done" | "failed"; at: string };

export type MealDay = { date: string; day: string; lunch?: string; dinner?: string };

// What saving the meals form sends: only the days shown, each replacing what was saved.
export type MealsRequest = { days: Record<string, { lunch?: string; dinner?: string }> };

// A new Google Calendar event: timed with "HH:MM" start and end, or all day.
export type NewEvent = { title: string; date: string } & ({ start: string; end: string } | { allDay: true });

export type GoalKind = "5k" | "10k" | "half" | "marathon" | "swim";

export type Goal = { name: string; kind: GoalKind; date: string }; // date is "YYYY-MM-DD"

// What saving the form sends: an event to train for, or { clear: true } for general fitness.
export type GoalRequest = Goal | { clear: true };

export type WorkoutKind = "run" | "swim" | "strength" | "calisthenics" | "sport" | "race";

// One of today's workouts. Older briefs have only the title and detail.
export type Workout = {
  kind?: WorkoutKind;
  title: string; // short, such as "Strength, push day"
  detail: string; // the suggested workout, shown when the line is opened
  minutes?: number;
  away?: boolean; // at the gym or pool
  done?: boolean; // Garmin recorded it, or it was checked off
};

// What checking a workout off (or back on) sends.
export type DoneRequest = { date: string; kind: WorkoutKind; done: boolean };

export type Training = {
  focus: string;
  today: Workout[];
  gymNext?: string; // such as "Tomorrow: gym, push day"
  why: string;
  week: { label: string; done: number; target: number }[];
  plan?: { day: string; date: string; items: string[]; today?: boolean }[];
  goal?: Goal;
};

export type StoryItem = { text: string; source: string; url: string; why?: string };

export type SourceState = "ok" | "stale" | "failed";

export type Brief = {
  date: string;
  generatedAt?: string;
  sample?: boolean;
  scores: { league: League; label: string; when: string; games: Score[] }[];
  weather?: {
    now: string;
    high: string;
    low: string;
    conditions: string;
    details: string;
    plan: string;
    alert?: string;
    trainingWindows: TrainingWindow[];
  };
  schedule?: ScheduleItem[];
  todos?: {
    list: string;
    receivedAt: string;
    items: { title: string; due?: string; notes?: string }[]; // due is "YYYY-MM-DD"
  };
  suggestions?: Suggestion[];
  replan?: Replan;
  meals?: MealDay[];
  training?: Training;
  teams?: { team: Team; update: string; next: string }[];
  listening?: {
    yesterday: { minutes: number; topArtist: string; topSong: string };
    soundtrack: { kind: string; title: string; artist: string; why: string; url: string };
  };
  words?: {
    english: { word: string; partOfSpeech: string; definition: string; example?: string };
    korean: { word: string; hanja: string; meaning: string; chain: string };
  };
  people?: { name: string; occasion: string; when: string }[];
  weekAhead?: { day: string; note: string }[];
  ski?: {
    summary: string;
    take: string;
    resorts: { name: string; base: string; new24h: string; new48h: string }[];
  };
  news?: { label: string; stories: StoryItem[] }[];
  roundup?: { label: string; text: string }[];
  sources: { name: string; state: SourceState; note: string }[];
};
