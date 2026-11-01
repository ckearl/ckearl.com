# Morning Brief backend

Builds the daily brief for `ckearl.com/morning-brief` and serves it behind a password.
Design: `docs/superpowers/specs/2026-10-31-morning-brief-design.md`.

    python3 -m pytest          # from this folder, with requirements-dev.txt installed
    scripts/deploy.sh          # builds and deploys with the hash from .env

`src/data/korean_words.json` comes from `hanja-chain-data`, adapted from 국립국어원's
dictionaries under CC BY-SA 2.0 KR.
