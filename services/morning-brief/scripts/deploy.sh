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
  "SpotifyClientId=${SPOTIFY_CLIENT_ID:-}" \
  "SpotifyClientSecret=${SPOTIFY_CLIENT_SECRET:-}" \
  "SpotifyRefreshToken=${SPOTIFY_REFRESH_TOKEN:-}" \
  "YouTubeApiKey=${YOUTUBE_API_KEY:-}" \
  "GoogleClientId=$GOOGLE_CLIENT_ID" \
  "GoogleClientSecret=$GOOGLE_CLIENT_SECRET" \
  "GoogleRefreshToken=$GOOGLE_REFRESH_TOKEN" \
  "TodosKeyHash=$TODOS_KEY_HASH" \
  "CalendarOwners=${CALENDAR_OWNERS:-}" \
  "GarminApiKey=$GARMIN_API_KEY" \
  "TrainingEasyPace=${TRAINING_EASY_PACE:-}" \
  "TrainingBaseMiles=${TRAINING_BASE_MILES:-7.5}" \
  "WorkHours=${WORK_HOURS:-Mon-Fri,08:00-17:00}" \
  "MorningHelp=${MORNING_HELP:-Mon-Fri,07:00-07:40}" \
  "AnthropicApiKey=$ANTHROPIC_API_KEY" \
  "$@"
