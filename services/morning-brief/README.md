# Morning Brief backend

Builds the daily brief for `ckearl.com/morning-brief` and serves it behind a password.
Design: `docs/superpowers/specs/2026-10-31-morning-brief-design.md`.

    python3 -m pytest          # from this folder, with requirements-dev.txt installed
    scripts/deploy.sh          # builds and deploys with the settings from .env

The page posts the password to `POST /brief/session` for a token that lasts 30 days, then sends
that token to `GET /brief/today`. Changing `BRIEF_TOKEN_SECRET` signs everyone out.

Listening comes from the `spotify_stats` snapshot in S3. The ski report only appears in season
when 8 or more inches is forecast for the Cottonwoods in the next three days.

`src/data/korean_words.json` comes from `hanja-chain-data`, adapted from 국립국어원's
dictionaries under CC BY-SA 2.0 KR.
