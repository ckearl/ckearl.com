# Morning Brief design

Status: approved in conversation on 2026-10-31. Page design reviewed by Christopher.

## What it is
A private daily page at `ckearl.com/morning-brief`. It replaces a scheduled Claude task whose
web searches produced thin, unreliable sections. Real APIs supply the facts, fixed rules make
the decisions, and Claude only ranks and explains.

## Goals
- Ready by the time Christopher wakes up, and readable on his phone.
- Sources fail one at a time. A failed source drops or shrinks its section and shows in Brief
  Status. It never blanks the page.
- Cheap and low maintenance: a separate AWS SAM stack in the style of `spotify_stats`.

## Non-goals
Sending or editing anything in Calendar, Reminders or Spotify. Gmail. Coaching or medical
advice. Automatic two-way Reminders sync.

## Architecture
```
EventBridge rule, 11:30 UTC (5:30 AM Mountain in summer, 4:30 AM in winter)
  -> generate Lambda -> sources, each in its own try/except
                     -> saves one JSON brief per date to DynamoDB (kept 90 days)
Next.js page -> password -> GET /brief/today -> api Lambda -> DynamoDB
iPhone Shortcut -> POST /todos, POST /work-calendar (stage 3)
```
The backend lives in `services/morning-brief`. The `Brief` type in
`lib/morning-brief/types.ts` is the contract between the two sides. Every section except
`date`, `scores` and `sources` is optional.

Secrets are stack parameters read from an untracked `.env`, as in `spotify_stats`. The API
checks a SHA-256 password hash in constant time, throttles requests, and allows only
ckearl.com and local preview origins.

## Sources
| Section | Source | Notes |
|---|---|---|
| Weather, alerts | NWS (`api.weather.gov`) | Provo grid point |
| Air quality, sunrise | Open-Meteo | No account |
| Scores, teams | ESPN public endpoints | Undocumented. One date per request; ranges return 400 |
| News | KSL, Deseret News, BBC, NPR RSS | Newest stories until Claude ranks them in stage 4 |
| English word | Wiktionary word of the day feed | |
| Korean word | Bundled list from `hanja-chain-data` | Learner words with English glosses |
| Listening, soundtrack | `spotify_stats` | Stage 3 |
| Calendars | Google Calendar read-only, plus iPhone Shortcut | Stage 3 |
| To-dos | Reminders through an iPhone Shortcut | Stage 3, depends on the locked-phone test |
| Recovery, workouts | Garmin Personal API, calendar | Stage 3, depends on the HRV and sleep test |
| Ski | NWS, snow stations, best-effort lifts | Stage 3, conditional as in the original brief |

## Scores strip
Every NBA and Premier League game, plus followed teams elsewhere. The followed list lives in
`services/morning-brief/src/brief/config.py`. NBA, NHL and MLB show the previous day. The NFL
and soccer leagues look back three days, because they don't play daily.

## Work calendar
Work data stays as busy blocks with no titles, and goes to the backend only if Marriott's
policy allows it.

## Training rules (stage 4)
Rules choose the plan. Claude writes the explanation and never changes the plan.
- Focus is required and an event is optional. With no event, run repeating four-week blocks:
  three build weeks and one easier week.
- With an event, count down to the date using the goal time or pace.
- Cardio is mostly running and swimming, at 3 to 4 runs for each swim.
- Strength once or twice a week, for shoulders, chest and vertical jump.
- 15 minutes of calisthenics every day.
- About 80% of cardio stays easy, weekly volume grows by about 10%, and hard days follow an
  easy day. Poor sleep or low HRV lowers intensity.
- Basketball and soccer on the calendar count toward load.
- Training slots are early morning, right after work, and night.

## Failure handling
Each source reports `ok`, `stale` or `failed` with a short note, shown in Brief Status. If
generation fails entirely, the API returns the newest saved brief and the page shows its date.

## Build order
1. Backend stack: store, API, password, schedule.
2. No-account sources: weather, air quality, scores, teams, news, words.
3. Personal sources: Spotify, calendars, Reminders, Garmin, ski.
4. Claude ranking and the training rules.
5. Saved input: focus, events, usual travel mode per place.
