# Morning Brief: training plan and Claude integration

Not started. This records the direction agreed on 2026-11-01. Design details are in
`docs/superpowers/specs/2026-10-31-morning-brief-design.md`.

## Order
1. Ship the waiting work: privacy and terms pages, Google Calendar, Gamecast links and
   minimizing windows. Fix the Word of the Day definition parser.
2. Reminders Shortcut, which the game plan depends on.
3. Garmin test. Day-of training adjustments need real workout data, so this comes before the
   training work.
4. Claude integration.
5. Training plan.

## Claude integration
Claude ranks the news, explains why stories matter, writes sports and AI headlines, chooses
the game plan, and writes the training explanation.

- **Cost goal:** free or nearly free. Start with Claude Haiku 5.5, and check its output on a
  week of real briefs before settling on it.
- **Estimate:** at 20,000 input and 4,000 output tokens a day, using prices dated 2026-10-06:
  | Model | Per day | Per month |
  |---|---|---|
  | Haiku 5.5 | about $0.004 | about $0.12 |
  | Sonnet 5.5 | about $0.08 | about $2.40 |
  | Opus 5.5 | about $0.16 | about $4.80 |
- **Billing:** the API is separate from a Claude subscription, so this needs an API account
  with credit. Set a low spending limit. The API key goes in `services/morning-brief/.env`.
- **Before sending calendar data:** update `/privacy`, which currently says calendar data isn't
  shared.
- **Untrusted text:** calendar, Reminders and news text is data, never instructions.

## Training plan
No model training is needed. Rules choose the workout, and Claude only writes a two-sentence
explanation. That costs nothing, can be tested, and can't improvise.

### Inputs
| Input | Source |
|---|---|
| Other activities (basketball, soccer) | Google Calendar |
| Sleep and HRV | Garmin |
| Completed workouts and their intensity | Garmin |
| Weekly volume, easy pace, focus | Saved settings, still needed from Christopher |

### Weekly plan, on Sunday
Fit runs, swims and strength around the calendar's other activities, and save the result as
data so the morning check has something to compare against. The page shows the week and what
changed.

- 3 to 4 runs for each swim.
- Strength once or twice a week, for shoulders, chest and vertical jump.
- 15 minutes of calisthenics every day.
- About 80% of cardio stays easy, and hard days follow an easy day.
- Weekly volume grows by about 10%, in blocks of three build weeks and one easier week.
- Training slots are early morning, right after work, and night.

### Morning check, daily
Compare yesterday's plan with what Garmin recorded, then check last night's sleep and HRV.

### Adjustment rules
| What happened | What changes |
|---|---|
| Workout came up short | Drop the missed work rather than cramming it in, and keep today as planned |
| Workout went harder than planned | Count it as the hard day, and turn the next hard session easy |
| Poor sleep or low HRV | Swap a hard session for an easy one |
| Unplanned game or activity | Count it as load, and move the next hard session back if needed |

### Notes
- An activity that's on both the calendar and Garmin counts once.
- Garmin shows what happened, not why. Add a one-tap "felt rough / fine / great" on the page
  after the basics work.
- Show an injury caution. This isn't coaching or medical advice.

### Open
- Whether Garmin's Personal API returns sleep, HRV and workout intensity. If not, the fallbacks
  are Strava for workouts or Health Auto Export for Apple Watch data.
- Current weekly mileage, swim volume and easy pace.

## Cut
Sports trade and signing rumors, which have no clean source. Keep injuries and completed trades.
