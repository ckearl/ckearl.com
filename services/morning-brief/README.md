# Morning Brief backend

Builds the daily brief for `ckearl.com/morning-brief` and serves it behind a password.
Design: `docs/superpowers/specs/2026-10-31-morning-brief-design.md`.

    python3 -m pytest          # from this folder, with requirements-dev.txt installed
    scripts/deploy.sh          # builds and deploys with the settings from .env

The page posts the password to `POST /brief/session` for a token that lasts 30 days, then sends
that token to `GET /brief/today`. Changing `BRIEF_TOKEN_SECRET` signs everyone out.

An iPhone Shortcut sends the Reminders list to `POST /brief/todos` before the brief runs, as
`{"items": [{"title", "due", "notes"}]}` with its own key, which can do nothing else.

Listening comes from the `spotify_stats` snapshot in S3. The ski report only appears in season
when 8 or more inches is forecast for the Cottonwoods in the next three days.

Calendar reads every calendar on the Google account with read-only access, skipping holidays
and birthdays, whether or not it's checked in the Google Calendar app. `CALENDAR_OWNERS` in
`.env` marks the calendars that are Senah's (`id=hers`), shared (`id=shared`) or left out
(`id=skip`). Everything else counts as mine. The page can show mine, hers or both.

The work Outlook calendar comes from a second Shortcut, which sends today's events from the
phone's calendar to `POST /brief/work` with the same key, as
`{"events": [{"start", "end", "allDay"}]}` with ISO 8601 times. Only the times are kept, and
the page shows each one as "Work". To connect it, create a Desktop OAuth client in a Google Cloud project
whose consent screen is In production (test-mode tokens expire after 7 days), then run
`python3 scripts/connect_google.py <downloaded client_secret file>`.

`src/data/korean_words.json` comes from `hanja-chain-data`, adapted from 국립국어원's
dictionaries under CC BY-SA 2.0 KR.
