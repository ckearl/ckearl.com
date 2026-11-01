#!/usr/bin/env bash
# Builds and deploys the stack with the settings from .env.
set -euo pipefail
cd "$(dirname "$0")/.."

set -a
source .env
set +a

sam build
sam deploy --parameter-overrides \
  "BriefPasswordHash=$BRIEF_PASSWORD_HASH" \
  "BriefTokenSecret=$BRIEF_TOKEN_SECRET" \
  "SpotifyBucket=$SPOTIFY_BUCKET" \
  "$@"
