import type { Team } from "@/lib/morning-brief/types";

export default function TeamMonogram({ team }: { team: Team }) {
  return (
    <span className="monogram" style={{ background: team.bg, color: team.fg }} aria-hidden="true">
      {team.abbr}
    </span>
  );
}
