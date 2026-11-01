import type { Brief } from "@/lib/morning-brief/types";

// Made-up data for reviewing the design. Scores, news and health numbers here
// are not real.
export const sampleBrief: Brief = {
  date: "2026-11-02",
  sample: true,
  scores: [
    {
      league: "nba",
      label: "NBA",
      when: "Sunday night",
      games: [
        { away: { abbr: "lal", name: "Lakers", score: 108 }, home: { abbr: "utah", name: "Jazz", score: 114 }, status: "Final" },
        { away: { abbr: "bos", name: "Celtics", score: 121 }, home: { abbr: "ny", name: "Knicks", score: 117 }, status: "Final" },
        { away: { abbr: "okc", name: "Thunder", score: 126 }, home: { abbr: "den", name: "Nuggets", score: 119 }, status: "Final/OT" },
        { away: { abbr: "gs", name: "Warriors", score: 102 }, home: { abbr: "phx", name: "Suns", score: 110 }, status: "Final" },
        { away: { abbr: "mia", name: "Heat", score: 99 }, home: { abbr: "mil", name: "Bucks", score: 105 }, status: "Final" },
        { away: { abbr: "por", name: "Blazers", score: 113 }, home: { abbr: "sa", name: "Spurs", score: 118 }, status: "Final" },
      ],
    },
    {
      league: "nfl",
      label: "NFL",
      when: "Sunday",
      games: [
        { away: { abbr: "sea", name: "Seahawks", score: 24 }, home: { abbr: "lar", name: "Rams", score: 20 }, status: "Final" },
        { away: { abbr: "sf", name: "49ers", score: 27 }, home: { abbr: "det", name: "Lions", score: 24 }, status: "Final" },
        { away: { abbr: "den", name: "Broncos", score: 17 }, home: { abbr: "kc", name: "Chiefs", score: 23 }, status: "Final" },
        { away: { abbr: "min", name: "Vikings", score: 30 }, home: { abbr: "gb", name: "Packers", score: 28 }, status: "Final/OT" },
        { away: { abbr: "bal", name: "Ravens", score: 31 }, home: { abbr: "pit", name: "Steelers", score: 16 }, status: "Final" },
        { away: { abbr: "buf", name: "Bills", score: 28 }, home: { abbr: "mia", name: "Dolphins", score: 13 }, status: "Final" },
      ],
    },
    {
      league: "nhl",
      label: "NHL",
      when: "Sunday night",
      games: [
        { away: { abbr: "bos", name: "Bruins", score: 3 }, home: { abbr: "tor", name: "Maple Leafs", score: 2 }, status: "Final/OT" },
        { away: { abbr: "chi", name: "Blackhawks", score: 1 }, home: { abbr: "col", name: "Avalanche", score: 4 }, status: "Final" },
        { away: { abbr: "vgk", name: "Golden Knights", score: 5 }, home: { abbr: "la", name: "Kings", score: 2 }, status: "Final" },
      ],
    },
    {
      league: "epl",
      label: "Premier League",
      when: "Saturday and Sunday",
      games: [
        { away: { abbr: "ars", name: "Arsenal", score: 1 }, home: { abbr: "tot", name: "Spurs", score: 2 }, status: "FT" },
        { away: { abbr: "che", name: "Chelsea", score: 1 }, home: { abbr: "liv", name: "Liverpool", score: 1 }, status: "FT" },
        { away: { abbr: "new", name: "Newcastle", score: 0 }, home: { abbr: "man", name: "Man United", score: 2 }, status: "FT" },
        { away: { abbr: "eve", name: "Everton", score: 2 }, home: { abbr: "mnc", name: "Man City", score: 3 }, status: "FT" },
        { away: { abbr: "ful", name: "Fulham", score: 0 }, home: { abbr: "avl", name: "Aston Villa", score: 0 }, status: "FT" },
        { away: { abbr: "lee", name: "Leeds", score: 1 }, home: { abbr: "bha", name: "Brighton", score: 2 }, status: "FT" },
      ],
    },
    {
      league: "laliga",
      label: "La Liga",
      when: "Saturday and Sunday",
      games: [
        { away: { abbr: "val", name: "Valencia", score: 0 }, home: { abbr: "rma", name: "Real Madrid", score: 3 }, status: "FT" },
        { away: { abbr: "bar", name: "Barcelona", score: 2 }, home: { abbr: "atm", name: "Atlético", score: 2 }, status: "FT" },
      ],
    },
    {
      league: "seriea",
      label: "Serie A",
      when: "Saturday and Sunday",
      games: [
        { away: { abbr: "juv", name: "Juventus", score: 1 }, home: { abbr: "int", name: "Inter", score: 1 }, status: "FT" },
        { away: { abbr: "nap", name: "Napoli", score: 2 }, home: { abbr: "mil", name: "Milan", score: 1 }, status: "FT" },
        { away: { abbr: "roma", name: "Roma", score: 3 }, home: { abbr: "laz", name: "Lazio", score: 1 }, status: "FT" },
      ],
    },
    {
      league: "bundesliga",
      label: "Bundesliga",
      when: "Saturday",
      games: [
        { away: { abbr: "dor", name: "Dortmund", score: 1 }, home: { abbr: "mun", name: "Bayern", score: 4 }, status: "FT" },
        { away: { abbr: "b04", name: "Leverkusen", score: 2 }, home: { abbr: "rbl", name: "Leipzig", score: 0 }, status: "FT" },
      ],
    },
    {
      league: "ligue1",
      label: "Ligue 1",
      when: "Sunday",
      games: [
        { away: { abbr: "olm", name: "Marseille", score: 0 }, home: { abbr: "psg", name: "PSG", score: 2 }, status: "FT" },
        { away: { abbr: "lyon", name: "Lyon", score: 1 }, home: { abbr: "nice", name: "Nice", score: 1 }, status: "FT" },
      ],
    },
    {
      league: "mlb",
      label: "MLB",
      when: "Design sample",
      games: [
        { away: { abbr: "wsh", name: "Nationals", score: 5 }, home: { abbr: "sea", name: "Mariners", score: 4 }, status: "Final" },
      ],
    },
  ],
  weather: {
    now: "34°",
    high: "52°",
    low: "31°",
    conditions: "Clear and calm",
    details: "5% rain, wind NW 6 mph, air quality good (AQI 41). Sunrise 7:10, sunset 5:32.",
    plan: "Gloves for an early run. A light jacket covers the rest of the day.",
    trainingWindows: [
      { label: "Early morning", time: "6:00–7:00 AM", conditions: "33°, calm, dark until 7:10" },
      { label: "After work", time: "5:15–6:15 PM", conditions: "47°, light wind, air still good", best: true },
      { label: "Night", time: "8:00–9:00 PM", conditions: "38°, calm, air slipping to moderate" },
    ],
  },
  schedule: [
    { start: "08:30", end: "09:00", title: "Busy", calendar: "work" },
    { start: "10:00", end: "11:00", title: "Busy", calendar: "work" },
    {
      start: "12:30",
      end: "13:30",
      title: "Lunch with a friend",
      calendar: "personal",
      place: "Downtown Provo",
      travel: { minutes: { walk: 22, bike: 9, drive: 7 }, mode: "walk" },
    },
    { start: "14:00", end: "15:30", title: "Busy", calendar: "work" },
    {
      start: "16:00",
      end: "16:45",
      title: "Haircut",
      calendar: "personal",
      place: "Orem",
      travel: { minutes: { walk: 74, bike: 31, drive: 16 }, mode: "drive" },
    },
    { start: "19:30", end: "21:00", title: "Basketball", calendar: "personal" },
  ],
  gamePlan: [
    { task: "Replace the furnace filter", estimate: "10 min", why: "Quick, and the first real cold nights are this week." },
    { task: "Blow out the sprinklers", estimate: "45 min", why: "Dry today, and overnight lows drop below 30 by Thursday." },
    { task: "Book the car inspection", estimate: "5 min", why: "You have a gap at 11:00." },
  ],
  training: {
    focus: "Build long-distance endurance",
    today: [
      { title: "Easy run, 5 miles", detail: "Conversational pace. Go after work, when it's warmest." },
      { title: "Calisthenics, 15 minutes", detail: "Three rounds: 12 pike push-ups, 15 push-ups, 10 squat jumps, 30-second plank." },
    ],
    why: "Basketball tonight counts as your hard effort, so the run stays easy. HRV is in its normal range and sleep was 7h 20m. Strength moves to Wednesday: shoulders, chest and box jumps.",
    week: [
      { label: "Runs", done: 0, target: 3 },
      { label: "Swims", done: 0, target: 1 },
      { label: "Strength", done: 0, target: 2 },
      { label: "Calisthenics", done: 0, target: 7 },
    ],
  },
  teams: [
    { team: { abbr: "UTA", name: "Utah Jazz", bg: "#4e008e", fg: "#ffffff" }, update: "Beat the Lakers 114–108. Now 3–3.", next: "Tue 7:00 PM vs Kings, KJZZ" },
    { team: { abbr: "UTA", name: "Utah Mammoth", bg: "#000000", fg: "#7ab2e1" }, update: "Off last night. Now 8–4–1.", next: "Tonight 7:30 PM at Avalanche, Utah16" },
    { team: { abbr: "RSL", name: "Real Salt Lake", bg: "#a32035", fg: "#ffffff" }, update: "Season over. Roster decisions are due this month.", next: "No match scheduled" },
    { team: { abbr: "BYU", name: "BYU", bg: "#0047ba", fg: "#ffffff" }, update: "Football won 31–24 on Saturday.", next: "Sat 1:30 PM at Baylor, ESPN2" },
    { team: { abbr: "TOT", name: "Tottenham", bg: "#ffffff", fg: "#0b1426" }, update: "Beat Arsenal 2–1. Up to 5th.", next: "Wed 1:00 PM vs Inter, Paramount+" },
  ],
  listening: {
    yesterday: { minutes: 212, topArtist: "Khruangbin", topSong: "Evan Finds the Third Room" },
    soundtrack: {
      kind: "Back in rotation",
      title: "Currents",
      artist: "Tame Impala",
      why: "You played it weekly in 2021 and not once since March. It suits an after-work run.",
      url: "https://open.spotify.com",
    },
  },
  words: {
    english: {
      word: "ebullient",
      partOfSpeech: "adjective",
      definition: "Cheerful and full of energy.",
      example: "The crowd stayed ebullient through double overtime.",
    },
    korean: {
      word: "입학",
      hanja: "入學",
      meaning: "Admission to a school",
      chain: "學 also appears in 학교 (學校), school.",
    },
  },
  people: [
    { name: "A friend", occasion: "Birthday", when: "Thursday" },
    { name: "A family member", occasion: "Anniversary", when: "In 9 days" },
  ],
  weekAhead: [
    { day: "Mon", note: "Busy afternoon. Easy run after work." },
    { day: "Wed", note: "Lightest work day. Best slot for strength." },
    { day: "Thu", note: "First hard freeze. Finish outdoor chores before it." },
    { day: "Sat", note: "BYU at 1:30 PM. Long run in the morning." },
  ],
  ski: {
    summary: "A storm could bring 8 to 12 inches to the Cottonwoods by Thursday.",
    take: "Resorts aren't open yet, so this is one to watch.",
    resorts: [
      { name: "Snowbird", base: '14"', new24h: '0"', new48h: '2"', lifts: "Closed" },
      { name: "Brighton", base: '11"', new24h: '0"', new48h: '1"', lifts: "Closed" },
      { name: "Solitude", base: '12"', new24h: '0"', new48h: '1"', lifts: "Closed" },
      { name: "Park City", base: '4"', new24h: '0"', new48h: '0"', lifts: "Closed" },
    ],
  },
  news: [
    {
      label: "Utah and US",
      stories: [
        { text: "Utah County commissioners take up a water conservation plan this week.", source: "KSL", url: "https://www.ksl.com" },
        { text: "State lawmakers preview a housing bill ahead of the January session.", source: "Deseret News", url: "https://www.deseret.com" },
        { text: "Federal Reserve officials signal they'll hold rates through the year.", source: "AP", url: "https://apnews.com" },
      ],
    },
    {
      label: "World",
      stories: [
        { text: "Trade talks resume in Geneva. A deal would lower tariffs on electronics.", source: "BBC", url: "https://www.bbc.com" },
        { text: "Climate negotiators arrive for the annual summit. Finance is the main fight.", source: "AP", url: "https://apnews.com" },
        { text: "Japan's new budget raises defense spending, shifting the regional balance.", source: "BBC", url: "https://www.bbc.com" },
      ],
    },
  ],
  roundup: [
    { label: "Sports", text: "The NBA Cup schedule tips off Friday. Champions League matchday 4 starts Tuesday." },
    { label: "AI and tech", text: "A sample line about this week's Anthropic and Claude news." },
    { label: "Markets", text: "S&P 500 up 0.4% on Friday. Informational only." },
    { label: "Roads", text: "I-15 southbound lane closure near Lehi from 9:00 PM to 5:00 AM." },
  ],
  sources: [
    { name: "Weather", state: "ok", note: "Updated 5:30 AM" },
    { name: "Calendars", state: "ok", note: "Updated 5:30 AM" },
    { name: "Reminders", state: "ok", note: "Pushed from iPhone at 5:28 AM" },
    { name: "Garmin", state: "stale", note: "Last sync 9:42 PM, so sleep may be incomplete" },
    { name: "Spotify", state: "ok", note: "Updated 5:30 AM" },
    { name: "Scores", state: "ok", note: "Updated 5:30 AM" },
    { name: "Ski report", state: "failed", note: "Lift data unavailable, using snow stations" },
  ],
};
