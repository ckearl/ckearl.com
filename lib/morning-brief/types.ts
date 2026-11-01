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

export type TravelMode = "walk" | "bike" | "drive";

export type ScheduleItem = {
  start: string; // 24-hour "HH:MM"
  end: string;
  title: string;
  calendar: "personal" | "work";
  allDay?: boolean;
  place?: string;
  travel?: { minutes: Record<TravelMode, number>; mode: TravelMode };
};

export type TrainingWindow = { label: string; time: string; conditions: string; best?: boolean };

export type StoryItem = { text: string; source: string; url: string };

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
  gamePlan?: { task: string; estimate: string; why: string }[];
  training?: {
    focus: string;
    today: { title: string; detail: string }[];
    why: string;
    week: { label: string; done: number; target: number }[];
  };
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
