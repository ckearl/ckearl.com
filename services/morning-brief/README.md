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

Calendar reads every calendar checked in Google Calendar with read-only access, skipping
holidays and birthdays. To connect it, create a Desktop OAuth client in a Google Cloud project
whose consent screen is In production (test-mode tokens expire after 7 days), then run
`python3 scripts/connect_google.py <downloaded client_secret file>`.

`src/data/korean_words.json` comes from `hanja-chain-data`, adapted from 국립국어원's
dictionaries under CC BY-SA 2.0 KR.
