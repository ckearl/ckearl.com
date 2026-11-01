import BriefWindow from "@/components/morning-brief/BriefWindow";
import DaySchedule from "@/components/morning-brief/DaySchedule";
import ScoresStrip from "@/components/morning-brief/ScoresStrip";
import TeamMonogram from "@/components/morning-brief/TeamMonogram";
import type { Brief } from "@/lib/morning-brief/types";

const stateLabels = { ok: "OK", stale: "Old", failed: "Failed" };

function dueLabel(due: string, today: string) {
  if (due < today) return "Overdue";
  if (due === today) return "Due today";
  return `Due ${new Date(`${due}T12:00:00`).toLocaleDateString("en-US", { month: "short", day: "numeric" })}`;
}

export default function BriefView({ brief, stale }: { brief: Brief; stale?: boolean }) {
  const dateLabel = new Date(`${brief.date}T12:00:00`).toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
  });
  const { todos, weather, training, listening, words, ski } = brief;

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
        {brief.schedule && (
          <BriefWindow title="Today">
            <DaySchedule items={brief.schedule} />
          </BriefWindow>
        )}

        {weather && (
          <BriefWindow title="Weather">
            <div className="weather-now">
              <p className="weather-temp">{weather.now}</p>
              <div>
                <p className="weather-conditions">{weather.conditions}</p>
                <p>High {weather.high}, low {weather.low}</p>
              </div>
            </div>
            <p>{weather.details}</p>
            <p className="lead-line">{weather.plan}</p>
            <h3>Best time to train outside</h3>
            <ul className="windows-list">
              {weather.trainingWindows.map((window) => (
                <li key={window.label} className={window.best ? "is-best" : ""}>
                  <strong>{window.label}, {window.time}</strong>
                  <span>{window.conditions}</span>
                </li>
              ))}
            </ul>
          </BriefWindow>
        )}

        {todos && (
          <BriefWindow title={todos.list}>
            {todos.items.length > 0 ? (
              <ul className="plan-list">
                {todos.items.map((item, index) => (
                  <li key={`${index}-${item.title}`}>
                    <p>
                      <strong>{item.title}</strong>
                      {item.due && <span className="muted"> ({dueLabel(item.due, brief.date)})</span>}
                    </p>
                    {item.notes && <p className="muted">{item.notes}</p>}
                  </li>
                ))}
              </ul>
            ) : (
              <p>Nothing left on the list.</p>
            )}
          </BriefWindow>
        )}

        {brief.gamePlan && (
          <BriefWindow title="Game Plan">
            <ul className="plan-list">
              {brief.gamePlan.map((item) => (
                <li key={item.task}>
                  <p><strong>{item.task}</strong> <span className="muted">({item.estimate})</span></p>
                  <p>{item.why}</p>
                </li>
              ))}
            </ul>
          </BriefWindow>
        )}

        {training && (
          <BriefWindow title="Training">
            <p className="muted">Focus: {training.focus}</p>
            <ul className="plan-list">
              {training.today.map((item) => (
                <li key={item.title}>
                  <p><strong>{item.title}</strong></p>
                  <p>{item.detail}</p>
                </li>
              ))}
            </ul>
            <p>{training.why}</p>
            <h3>This week</h3>
            <dl className="week-meters">
              {training.week.map((item) => (
                <div key={item.label}>
                  <dt>{item.label}</dt>
                  <dd>{item.done} of {item.target}</dd>
                  <span className="bar" aria-hidden="true">
                    <span style={{ width: `${(item.done / item.target) * 100}%` }} />
                  </span>
                </div>
              ))}
            </dl>
            <details className="goal-form">
              <summary>Change focus or add an event</summary>
              <form>
                <label>Focus or event name<input type="text" placeholder="Run farther" /></label>
                <label>Event date (optional)<input type="date" /></label>
                <label>Goal time or pace (optional)<input type="text" placeholder="8:30 per mile" /></label>
                <button type="button" className="gel-button" disabled>Save (not connected yet)</button>
              </form>
            </details>
          </BriefWindow>
        )}

        {brief.people && (
          <BriefWindow title="Coming Up">
            <ul className="people-list">
              {brief.people.map((person) => (
                <li key={person.name}>
                  <strong>{person.name}</strong>
                  <span>{person.occasion}, {person.when}</span>
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
          </BriefWindow>
        )}

        {brief.roundup && (
          <BriefWindow title="Also Worth Knowing">
            <dl className="roundup">
              {brief.roundup.map((item) => (
                <div key={item.label}>
                  <dt>{item.label}</dt>
                  <dd>{item.text}</dd>
                </div>
              ))}
            </dl>
          </BriefWindow>
        )}

        {brief.news && (
          <BriefWindow title="News">
            {brief.news.map((group) => (
              <div key={group.label} className="news-group">
                <h3>{group.label}</h3>
                <ul>
                  {group.stories.map((story) => (
                    <li key={story.text}>
                      {story.text} <a href={story.url}>{story.source}</a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </BriefWindow>
        )}

        {brief.teams && (
          <BriefWindow title="My Teams">
            <ul className="team-list">
              {brief.teams.map(({ team, update, next }) => (
                <li key={team.name}>
                  <TeamMonogram team={team} />
                  <div>
                    <p><strong>{team.name}</strong></p>
                    <p>{update}</p>
                    <p className="muted">Next: {next}</p>
                  </div>
                </li>
              ))}
            </ul>
          </BriefWindow>
        )}

        {ski && (
          <BriefWindow title="Ski Report">
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
          </BriefWindow>
        )}

        {listening && (
          <BriefWindow title="Today's Soundtrack">
            <p className="muted">{listening.soundtrack.kind}</p>
            <p className="soundtrack-title">{listening.soundtrack.title}</p>
            <p><strong>{listening.soundtrack.artist}</strong></p>
            <p>{listening.soundtrack.why}</p>
            <div className="info-links">
              <a href={listening.soundtrack.url} className="gel-button">Open in Spotify</a>
            </div>
            <h3>Yesterday</h3>
            {listening.yesterday.minutes > 0 ? (
              <p>
                {listening.yesterday.minutes} minutes. Top artist was {listening.yesterday.topArtist}, and your top song was
                &ldquo;{listening.yesterday.topSong}.&rdquo;
              </p>
            ) : (
              <p>No listening yesterday.</p>
            )}
          </BriefWindow>
        )}

        {words && (
          <BriefWindow title="Words of the Day">
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
                <p className="muted" lang="en">{words.korean.chain}</p>
              </div>
            </div>
          </BriefWindow>
        )}

        <BriefWindow title="Brief Status">
          <ul className="status-list">
            {brief.sources.map((source) => (
              <li key={source.name}>
                <span className={`status-dot is-${source.state}`}>{stateLabels[source.state]}</span>
                <strong>{source.name}</strong>
                <span>{source.note}</span>
              </li>
            ))}
          </ul>
        </BriefWindow>
      </main>
    </>
  );
}
