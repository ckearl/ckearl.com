# Morning Brief backend

Builds the daily brief for `ckearl.com/morning-brief` and serves it behind a password.
Design: `docs/superpowers/specs/2026-10-31-morning-brief-design.md`.

    python3 -m pytest          # from this folder, with requirements-dev.txt installed
    scripts/deploy.sh          # builds and deploys with the settings from .env

The page posts the password to `POST /brief/session` for a token that lasts 30 days, then sends
that token to `GET /brief/today`. Changing `BRIEF_TOKEN_SECRET` signs everyone out.

An iPhone Shortcut sends the Reminders list to `POST /brief/todos` before the brief runs, as
`{"items": [{"title", "due", "notes"}]}` with its own key, which can do nothing else. The page
doesn't list them; the day plan picks up to two. A duration in a reminder's notes, such as
"25 min, drive to the recycling center", is the least time it's given.

Listening comes from the `spotify_stats` snapshot in S3. The ski report only appears in season
when 8 or more inches is forecast for the Cottonwoods in the next three days.

Calendar reads every calendar on the Google account, skipping holidays and birthdays, whether
or not it's checked in the Google Calendar app. `CALENDAR_OWNERS` in `.env` marks the calendars
that are Senah's (`id=hers`), shared (`id=shared`) or left out (`id=skip`). Everything else
counts as mine. The page can show mine, hers or both. It can also add an event to the primary
calendar (`POST /brief/event`, with the page's login token), the only change it ever makes.
To connect Google, create a Desktop OAuth client in a Google Cloud project whose consent screen
is In production (test-mode tokens expire after 7 days), then run
`python3 scripts/connect_google.py <downloaded client_secret file>`. Run it with no file to
sign in again with the client already in `.env`.

The work Outlook calendar can't be read: the employer blocks phone sign-in and publishing. The
brief blocks out the usual work hours from `WORK_HOURS` (`Mon-Fri,08:00-17:00`) instead. If real
meeting times are ever sent to `POST /brief/work` (`{"events": [{"start", "end", "allDay"}]}`
with ISO 8601 times and the Shortcut key), they're used while under a day old. Only times are
kept, and the page shows each one as "Work". `MORNING_HELP` (`Mon-Fri,07:00-07:40`) holds the
morning stretch spent helping Senah get out the door, at its longest, so nothing is planned over it.

Claude suggests times for the day in the Today window: each workout on its own, music practice,
cooking and cleaning up dinner, 20 minutes of chores, reading, reminders that fit, and grocery runs
and meal prep based on the meals written on the page (`POST /brief/meals`). Every suggestion is
checked against my and shared events and dropped if it overlaps. Gym and pool workouts get 15
minutes of travel each way. Tapping a suggestion shows a button to add it to the calendar.

Training plans each week from the event saved on the page (`POST /brief/goal`, with the page's
login token), sports on my calendars, and the last month of Garmin runs, sleep and HRV through
Garmin's Personal API (`GARMIN_API_KEY`). Saving an event replans that day's brief right away.
Strength is two gym days a week, a push day and a full-body day, kept off run days when there's
room. Calisthenics is a daily habit in the morning, or right after an easy run. A workout counts
as done when Garmin records it (calisthenics recorded as HIIT counts) or when it's checked off on
the page (`POST /brief/done`, `{"date", "kind", "done"}`).
Easy pace and the fallback weekly miles are `TRAINING_EASY_PACE` and `TRAINING_BASE_MILES` in
`.env`.

`src/data/korean_words.json` comes from `hanja-chain-data`, adapted from 국립국어원's
dictionaries under CC BY-SA 2.0 KR.
