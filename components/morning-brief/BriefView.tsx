import DaySchedule, { type AddEvent, type MarkSuggestion, type ReplanDay } from "@/components/morning-brief/DaySchedule";
import MealPlan, { type SaveMeals } from "@/components/morning-brief/MealPlan";
import ScoresStrip from "@/components/morning-brief/ScoresStrip";
import TeamMonogram from "@/components/morning-brief/TeamMonogram";
import TrainingPlan, { type MarkDone } from "@/components/morning-brief/TrainingPlan";
import WindowStack, { type Pane } from "@/components/morning-brief/WindowStack";
import type { Brief, GoalRequest } from "@/lib/morning-brief/types";

const stateLabels = { ok: "OK", stale: "Old", failed: "Failed" };

export default function BriefView({
  brief,
  stale,
  onSaveGoal,
  onSaveMeals,
  onAddEvent,
  onMarkDone,
  onMarkSuggestion,
  onReplan,
}: {
  brief: Brief;
  stale?: boolean;
  onSaveGoal?: (goal: GoalRequest) => Promise<boolean>;
  onSaveMeals?: SaveMeals;
  onAddEvent?: AddEvent;
  onMarkDone?: MarkDone;
  onMarkSuggestion?: MarkSuggestion;
  onReplan?: ReplanDay;
}) {
  const dateLabel = new Date(`${brief.date}T12:00:00`).toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
  });
  const { weather, training, meals, listening, words, ski } = brief;
  const best = weather?.trainingWindows.find((window) => window.best);

  const panes = [
    brief.schedule && {
      id: "today",
      title: "Today",
      content: (
        <>
          <DaySchedule
            items={brief.schedule}
            suggestions={brief.suggestions}
            date={brief.date}
            replan={brief.replan}
            onAddEvent={onAddEvent}
            onMarkSuggestion={onMarkSuggestion}
            onReplan={onReplan}
          />
        </>
      ),
    },
    weather && {
      id: "weather",
      title: "Weather",
      content: (
        <>
          <div className="weather-now">
            <p className="weather-temp">{weather.now}</p>
            <div>
              <p className="weather-conditions">{weather.conditions}</p>
              <p>
                High {weather.high}, low {weather.low}
              </p>
            </div>
          </div>
          <p>{weather.details}</p>
          <p className="lead-line">{weather.plan}</p>
          {weather.trainingWindows.length > 0 ? (
            <details className="expander">
              <summary>
                Best time to train outside
                {best && (
                  <span>
                    : {best.label.toLowerCase()}, {best.time}
                  </span>
                )}
              </summary>
              <ul className="windows-list">
                {weather.trainingWindows.map((window) => (
                  <li key={window.label} className={window.best ? "is-best" : ""}>
                    <strong>
                      {window.label}, {window.time}
                    </strong>
                    <span>{window.conditions}</span>
                  </li>
                ))}
              </ul>
            </details>
          ) : (
            <p className="muted">Your calendar fills the usual training times today.</p>
          )}
        </>
      ),
    },
    training && {
      id: "training",
      title: "Training",
      content: (
        <>
          <TrainingPlan training={training} date={brief.date} onSaveGoal={onSaveGoal} onMarkDone={onMarkDone} />
        </>
      ),
    },
    meals && {
      id: "meals",
      title: "Meals",
      content: (
        <>
          <MealPlan meals={meals} onSave={onSaveMeals} />
        </>
      ),
    },
    brief.people && {
      id: "coming-up",
      title: "Coming Up",
      content: (
        <>
          <ul className="people-list">
            {brief.people.map((person) => (
              <li key={person.name}>
                <strong>{person.name}</strong>
                <span>
                  {person.occasion}, {person.when}
                </span>
              </li>
            ))}
          </ul>
          {brief.weekAhead && (
            <>
              <h3>Week ahead (Sundays)</h3>
              <ul className="week-list">
                {brief.weekAhead.map((day) => (
                  <li key={day.day}>
                    <strong>{day.day}</strong>
                    <span>{day.note}</span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </>
      ),
    },
    brief.roundup && {
      id: "roundup",
      title: "Also Worth Knowing",
      content: (
        <>
          <dl className="roundup">
            {brief.roundup.map((item) => (
              <div key={item.label}>
                <dt>{item.label}</dt>
                <dd>{item.text}</dd>
              </div>
            ))}
          </dl>
        </>
      ),
    },
    brief.news && {
      id: "news",
      title: "News",
      content: (
        <>
          {brief.news.map((group) => (
            <div key={group.label} className="news-group">
              <h3>{group.label}</h3>
              <ul>
                {group.stories.map((story) => (
                  <li key={story.text}>
                    {story.text} <a href={story.url}>{story.source}</a>
                    {story.why && <p className="muted">{story.why}</p>}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </>
      ),
    },
    brief.teams && {
      id: "teams",
      title: "My Teams",
      content: (
        <>
          <ul className="team-list">
            {brief.teams.map(({ team, update, next }) => (
              <li key={team.name}>
                <TeamMonogram team={team} />
                <div>
                  <p>
                    <strong>{team.name}</strong>
                  </p>
                  <p>{update}</p>
                  <p className="muted">Next: {next}</p>
                </div>
              </li>
            ))}
          </ul>
        </>
      ),
    },
    ski && {
      id: "ski",
      title: "Ski Report",
      content: (
        <>
          <p>{ski.summary}</p>
          <table className="ski-table">
            <thead>
              <tr>
                <th scope="col">Resort</th>
                <th scope="col">Base</th>
                <th scope="col">24h</th>
                <th scope="col">48h</th>
              </tr>
            </thead>
            <tbody>
              {ski.resorts.map((resort) => (
                <tr key={resort.name}>
                  <th scope="row">{resort.name}</th>
                  <td>{resort.base}</td>
                  <td>{resort.new24h}</td>
                  <td>{resort.new48h}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="lead-line">{ski.take}</p>
        </>
      ),
    },
    listening && {
      id: "soundtrack",
      title: "Today's Soundtrack",
      content: (
        <>
          <p className="muted">{listening.soundtrack.kind}</p>
          <p className="soundtrack-title">{listening.soundtrack.title}</p>
          <p>
            <strong>{listening.soundtrack.artist}</strong>
          </p>
          <p>{listening.soundtrack.why}</p>
          <div className="info-links">
            <a href={listening.soundtrack.url} className="gel-button">
              Open in Spotify
            </a>
          </div>
          <h3>Yesterday</h3>
          {listening.yesterday.minutes > 0 ? (
            <p>
              {listening.yesterday.minutes} minutes. Top artist was {listening.yesterday.topArtist}, and your top song
              was &ldquo;
              {listening.yesterday.topSong}.&rdquo;
            </p>
          ) : (
            <p>No listening yesterday.</p>
          )}
        </>
      ),
    },
    words && {
      id: "words",
      title: "Words of the Day",
      content: (
        <>
          <div className="word-pair">
            <div>
              <p className="word">{words.english.word}</p>
              <p className="muted">{words.english.partOfSpeech}</p>
              <p>{words.english.definition}</p>
              {words.english.example && <p className="muted">{words.english.example}</p>}
            </div>
            <div lang="ko">
              <p className="word word-korean">{words.korean.word}</p>
              <p className="muted">{words.korean.hanja}</p>
              <p lang="en">{words.korean.meaning}</p>
              <p className="muted" lang="en">
                {words.korean.chain}
              </p>
            </div>
          </div>
        </>
      ),
    },
    {
      id: "status",
      title: "Brief Status",
      content: (
        <>
          <ul className="status-list">
            {brief.sources.map((source) => (
              <li key={source.name}>
                <span className={`status-dot is-${source.state}`}>{stateLabels[source.state]}</span>
                <strong>{source.name}</strong>
                <span>{source.note}</span>
              </li>
            ))}
          </ul>
        </>
      ),
    },
  ].filter(Boolean) as Pane[];

  return (
    <>
      <nav className="menu-bar" aria-label="Main">
        <span className="menu-mark brief-mark">ck</span>
        <h1 className="brief-title">Morning Brief</h1>
        <span className="menu-clock brief-date">{dateLabel}</span>
      </nav>

      {brief.sample && <p className="sample-note">Sample data for reviewing the design. None of this is real yet.</p>}
      {stale && <p className="sample-note">This is the newest brief available, from {dateLabel}.</p>}

      <ScoresStrip scores={brief.scores} />

      <main className="brief">
        <WindowStack panes={panes} />
      </main>
    </>
  );
}
