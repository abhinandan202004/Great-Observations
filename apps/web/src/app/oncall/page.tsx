"use client";

import { type FormEvent, useEffect, useId, useMemo, useRef, useState } from "react";
import { getJson, putJson } from "@/lib/api";
import type { Team } from "@/lib/incidents";
import { move, type Person, type TeamOnCall, type UndeliveredEmail } from "@/lib/oncall";
import { useUserInvalid } from "@/lib/user-invalid";

export default function OnCallPage() {
  const [teams, setTeams] = useState<TeamOnCall[] | null>(null);
  const [people, setPeople] = useState<Team[]>([]);
  const [mail, setMail] = useState<UndeliveredEmail[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getJson<TeamOnCall[]>("/oncall")
      .then(setTeams)
      .catch((reason) => setError(String(reason)));
    getJson<Team[]>("/teams")
      .then(setPeople)
      .catch(() => setPeople([]));
    // Only the Admin may read the outbox; everyone else simply does not see this list.
    getJson<UndeliveredEmail[]>("/outbox/undelivered")
      .then(setMail)
      .catch(() => setMail(null));
  }, []);

  return (
    <main className="shell wide">
      <h1>On-call</h1>
      {error && <p role="alert">{error}</p>}
      {teams && <p>Fields marked * are required.</p>}
      {teams?.map((team) => (
        <TeamRotation
          key={team.team_id}
          team={team}
          members={people.find((p) => p.id === team.team_id)?.members ?? []}
          onSaved={(saved) =>
            setTeams((all) => all?.map((t) => (t.team_id === saved.team_id ? saved : t)) ?? null)
          }
        />
      ))}
      {mail && <Undelivered mail={mail} />}
    </main>
  );
}

function TeamRotation({
  team,
  members,
  onSaved,
}: {
  team: TeamOnCall;
  members: Team["members"];
  onSaved: (team: TeamOnCall) => void;
}) {
  const id = useId();
  const form = useRef<HTMLFormElement>(null);
  const candidate = useRef<HTMLSelectElement>(null);
  useUserInvalid(form);
  const [order, setOrder] = useState<Pick<Person, "id" | "display_name">[]>(
    team.rotation?.members ?? [],
  );
  const [announcement, setAnnouncement] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const zones = useMemo(() => Intl.supportedValuesOf("timeZone"), []);
  const absent = members.filter((m) => !order.some((o) => o.id === m.id));

  // React keeps each item's node and moves it, so focus stays on the button that was pressed.
  function shift(index: number, by: -1 | 1) {
    const to = index + by;
    if (to < 0 || to >= order.length) return;
    setOrder(move(order, index, to));
    setAnnouncement(`${order[index].display_name} moved to position ${to + 1} of ${order.length}.`);
  }

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const fields = new FormData(event.currentTarget);
    try {
      const saved = await putJson<TeamOnCall>(`/teams/${team.team_id}/oncall`, {
        members: order.map((m) => m.id),
        handover_local: `${fields.get("handover")}:00`,
        time_zone: fields.get("time_zone"),
        shift_days: Number(fields.get("shift_days")),
      });
      onSaved(saved);
      setError("");
      setStatus(`Saved the ${team.team} rotation.`);
    } catch (reason) {
      setError(String(reason));
    }
  }

  const ends = team.shift_ends_at && new Date(team.shift_ends_at);
  return (
    <article className="task" aria-labelledby={`${id}-heading`}>
      <h2 id={`${id}-heading`}>{team.team}</h2>
      {team.on_call && ends ? (
        <p>
          On call now: <strong>{team.on_call.display_name}</strong>, until{" "}
          <time dateTime={team.shift_ends_at!}>{ends.toLocaleString()}</time>
        </p>
      ) : (
        <p className="breach">
          <strong>Warning: no one is on call.</strong> Incident email reaches {team.group_email}{" "}
          only, and the Admin is told.
        </p>
      )}
      <form ref={form} className="stack" onSubmit={save} aria-labelledby={`${id}-heading`}>
        <fieldset>
          <legend>Rotation order</legend>
          {order.length === 0 && <p className="status">Nobody in the rotation yet.</p>}
          <ol className="rotation">
            {order.map((member, index) => (
              <li key={member.id}>
                <span>{member.display_name}</span>{" "}
                {/* aria-disabled, not disabled: a button at the end keeps focus after a move. */}
                <button
                  type="button"
                  aria-disabled={index === 0}
                  onClick={() => shift(index, -1)}
                  aria-label={`Move up ${member.display_name}`}
                >
                  Move up
                </button>{" "}
                <button
                  type="button"
                  aria-disabled={index === order.length - 1}
                  onClick={() => shift(index, 1)}
                  aria-label={`Move down ${member.display_name}`}
                >
                  Move down
                </button>{" "}
                <button
                  type="button"
                  onClick={() => {
                    setOrder(order.filter((o) => o.id !== member.id));
                    setAnnouncement(`${member.display_name} removed from the rotation.`);
                  }}
                  aria-label={`Remove ${member.display_name}`}
                >
                  Remove
                </button>
              </li>
            ))}
          </ol>
          <p className="visually-hidden" role="status">
            {announcement}
          </p>
          {absent.length > 0 && (
            <div className="filters">
              <label htmlFor={`${id}-add`}>Team member</label>
              <select id={`${id}-add`} ref={candidate}>
                {absent.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.display_name}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={() => {
                  const added = absent.find((m) => m.id === candidate.current?.value);
                  if (!added) return;
                  setOrder([...order, added]);
                  setAnnouncement(`${added.display_name} added at position ${order.length + 1}.`);
                }}
              >
                Add to rotation
              </button>
            </div>
          )}
        </fieldset>
        <div className="field">
          <label htmlFor={`${id}-handover`}>
            First handover <span aria-hidden="true">*</span>
          </label>
          <input
            id={`${id}-handover`}
            name="handover"
            type="datetime-local"
            required
            data-error={`${id}-handover-error`}
            defaultValue={team.rotation?.handover_local.slice(0, 16)}
          />
          <p id={`${id}-handover-error`} className="error-msg">
            <span role="img" aria-label="Error">
              ✖
            </span>{" "}
            First handover is required.
          </p>
        </div>
        <div className="field">
          <label htmlFor={`${id}-zone`}>
            Time zone of the handover <span aria-hidden="true">*</span>
          </label>
          <input
            id={`${id}-zone`}
            name="time_zone"
            list={`${id}-zones`}
            required
            autoComplete="off"
            spellCheck={false}
            data-error={`${id}-zone-error`}
            defaultValue={team.rotation?.time_zone ?? "UTC"}
          />
          <datalist id={`${id}-zones`}>
            {["UTC", ...zones].map((zone) => (
              <option key={zone} value={zone} />
            ))}
          </datalist>
          <p id={`${id}-zone-error`} className="error-msg">
            <span role="img" aria-label="Error">
              ✖
            </span>{" "}
            Time zone is required.
          </p>
        </div>
        <div className="field">
          <label htmlFor={`${id}-days`}>
            Shift length in days <span aria-hidden="true">*</span>
          </label>
          <input
            id={`${id}-days`}
            name="shift_days"
            type="number"
            min={1}
            max={28}
            required
            data-error={`${id}-days-error`}
            defaultValue={team.rotation?.shift_days ?? 7}
          />
          <p id={`${id}-days-error`} className="error-msg">
            <span role="img" aria-label="Error">
              ✖
            </span>{" "}
            Shift length must be 1 to 28 days.
          </p>
        </div>
        <button type="submit">Save rotation</button>
      </form>
      <p role="status">{status}</p>
      {error && <p role="alert">{error}</p>}
    </article>
  );
}

function Undelivered({ mail }: { mail: UndeliveredEmail[] }) {
  return (
    <section aria-labelledby="undelivered-heading">
      <h2 id="undelivered-heading">Undelivered email</h2>
      {mail.length === 0 ? (
        <p className="status">All email has been delivered.</p>
      ) : (
        <table>
          <caption>Email still waiting to be sent, oldest first</caption>
          <thead>
            <tr>
              <th scope="col">Subject</th>
              <th scope="col">To</th>
              <th scope="col">Attempts</th>
              <th scope="col">Next attempt</th>
              <th scope="col">Last error</th>
            </tr>
          </thead>
          <tbody>
            {mail.map((m) => (
              <tr key={m.id}>
                <td>{m.subject}</td>
                <td>{m.to_addresses.join(", ")}</td>
                <td>{m.attempts}</td>
                <td>
                  <time dateTime={m.next_attempt_at}>
                    {new Date(m.next_attempt_at).toLocaleString()}
                  </time>
                </td>
                <td>{m.last_error}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
