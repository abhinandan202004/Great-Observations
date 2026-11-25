"use client";

import { useParams } from "next/navigation";
import { type FormEvent, useEffect, useState } from "react";
import { LiveStatus } from "../../live-status";
import { getJson, postJson } from "@/lib/api";
import { useLive } from "@/lib/live";
import {
  type Detail,
  moves,
  SEVERITIES,
  STATES,
  type Summary,
  type Team,
  type TeamTask,
} from "@/lib/incidents";
import { AlertFigure } from "../../drafts/alert-figure";
import { Clock } from "../clock";
import { Attachments } from "./attachments";
import { RunbookPanel } from "./runbook";

type Act = (path: string, body: unknown) => Promise<void>;

export function Incident() {
  const { id } = useParams<{ id: string }>();
  const [incident, setIncident] = useState<Summary | Detail | null>(null);
  const [teams, setTeams] = useState<Team[]>([]);
  const [error, setError] = useState("");
  // Any change by anyone, anywhere, brings a refetch; so does catching up after a dropped link.
  const { live, version, notice } = useLive(id);

  useEffect(() => {
    let latest = true; // a slower, older answer must not overwrite a newer one
    getJson<Summary | Detail>(`/incidents/${id}`)
      .then((found) => {
        if (!latest) return;
        setIncident(found);
        // Only roles that see the detail may list teams; the summary view needs none.
        if ("teams" in found) return getJson<Team[]>("/teams").then((t) => latest && setTeams(t));
      })
      .catch((reason) => latest && setError(String(reason)));
    return () => {
      latest = false;
    };
  }, [id, version]);

  // Every change returns the updated incident, so the page redraws from the API's answer.
  const act: Act = async (path, body) => {
    try {
      setIncident(await postJson<Detail>(`/incidents/${id}${path}`, body));
      setError("");
    } catch (reason) {
      setError(String(reason));
    }
  };

  if (!incident) {
    return <main className="shell wide">{error ? <p role="alert">{error}</p> : "Loading…"}</main>;
  }
  return (
    <main className="shell wide">
      <h1>
        #{incident.number} {incident.title}
      </h1>
      <LiveStatus live={live} notice={notice} />
      <p>
        <strong>{incident.severity}</strong> · {incident.service} · raised{" "}
        {new Date(incident.raised_at).toLocaleString()}
      </p>
      <StatusBar current={incident.status} />
      {error && <p role="alert">{error}</p>}
      <p>
        <strong>Impact:</strong> {incident.impact}
      </p>
      <p>
        Acknowledge: <Clock timer={incident.acknowledge} /> · Resolve:{" "}
        <Clock timer={incident.resolve} />
      </p>
      {"teams" in incident && <Work incident={incident} teams={teams} act={act} version={version} />}
    </main>
  );
}

function StatusBar({ current }: { current: Summary["status"] }) {
  const reached = STATES.indexOf(current);
  return (
    <ol className="status-bar" aria-label="Status">
      {STATES.map((state, index) => (
        <li
          key={state}
          aria-current={state === current ? "step" : undefined}
          className={index < reached ? "done" : undefined}
        >
          {state}
        </li>
      ))}
    </ol>
  );
}

function Work({
  incident,
  teams,
  act,
  version,
}: {
  incident: Detail;
  teams: Team[];
  act: Act;
  version: number;
}) {
  const offered = moves(incident.status);
  const absent = teams.filter((team) => !incident.teams.some((t) => t.team_id === team.id));
  const closed = incident.status === "closed";

  function withReason(path: string, status: string) {
    return (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      const form = new FormData(event.currentTarget);
      act(path, { status: form.get("status") ?? status, reason: form.get("reason") });
    };
  }

  return (
    <>
      <section aria-label="Change status" className="filters">
        {offered.forward && (
          <button type="button" onClick={() => act("/status", { status: offered.forward })}>
            Move to {offered.forward}
          </button>
        )}
        {offered.back.length > 0 && (
          <form onSubmit={withReason("/status", "")}>
            <select name="status" aria-label="Earlier state">
              {offered.back.map((state) => (
                <option key={state}>{state}</option>
              ))}
            </select>{" "}
            <input name="reason" required placeholder="Reason" aria-label="Reason" />{" "}
            <button type="submit">Move back</button>
          </form>
        )}
        {offered.callerOnly && (
          <>
            <button type="button" onClick={() => act("/status", { status: "closed" })}>
              Close incident
            </button>
            <form onSubmit={withReason("/status", "investigating")}>
              <input name="reason" required placeholder="Why it is not fixed" aria-label="Reason" />{" "}
              <button type="submit">Reject resolution</button>
            </form>
          </>
        )}
        {!closed && (
          <form
            onSubmit={(event) => {
              event.preventDefault();
              act("/severity", { severity: new FormData(event.currentTarget).get("severity") });
            }}
          >
            <select name="severity" aria-label="Severity" defaultValue={incident.severity}>
              {SEVERITIES.map((severity) => (
                <option key={severity}>{severity}</option>
              ))}
            </select>{" "}
            <button type="submit">Change severity</button>
          </form>
        )}
      </section>

      <h2>Description</h2>
      <p className="prose">{incident.description}</p>
      <p className="status">Raised by {incident.caller}</p>

      {incident.alerts.length > 0 && (
        <>
          <h2>Alerts</h2>
          {incident.alerts.map((alert) => (
            <AlertFigure key={alert.breach_started_at} alert={alert} service={incident.service} />
          ))}
        </>
      )}

      <RunbookPanel incidentId={incident.id} status={incident.status} version={version} />

      <Attachments
        incidentId={incident.id}
        service={incident.service}
        raisedAt={incident.raised_at}
        open={!closed}
        version={version}
      />

      <h2>Teams</h2>
      {incident.teams.map((task) => (
        <Task
          key={task.team_id}
          task={task}
          team={teams.find((t) => t.id === task.team_id)}
          act={act}
          closed={closed}
        />
      ))}
      {!closed && absent.length > 0 && (
        <form
          onSubmit={(event) => {
            event.preventDefault();
            act("/teams", { team_id: new FormData(event.currentTarget).get("team_id") });
          }}
        >
          <select name="team_id" aria-label="Team to add">
            {absent.map((team) => (
              <option key={team.id} value={team.id}>
                {team.name}
              </option>
            ))}
          </select>{" "}
          <button type="submit">Add team</button>
        </form>
      )}

      <h2>Timeline</h2>
      <table>
        <thead>
          <tr>
            <th>When</th>
            <th>Who</th>
            <th>Change</th>
            <th>Reason</th>
          </tr>
        </thead>
        <tbody>
          {incident.timeline.map((event) => (
            <tr key={event.id}>
              <td>{new Date(event.time).toLocaleString()}</td>
              <td>{event.actor}</td>
              <td>
                {event.from_status ? `${event.from_status} → ` : ""}
                {event.to_status}
                {event.reopens !== null && " (rejected the resolution)"}
              </td>
              <td>{event.reason}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {incident.escalations.length > 0 && (
        <>
          <h2>Escalations</h2>
          <ol>
            {incident.escalations.map((e) => (
              <li key={`${e.team}-${e.step}`}>
                <time dateTime={e.time}>{new Date(e.time).toLocaleString()}</time>: not
                acknowledged, so {e.team} passed it from {e.from_person} to {e.to_person}{" "}
                (escalation {e.step})
              </li>
            ))}
          </ol>
        </>
      )}
    </>
  );
}

function Task({
  task,
  team,
  act,
  closed,
}: {
  task: TeamTask;
  team: Team | undefined;
  act: Act;
  closed: boolean;
}) {
  const base = `/teams/${task.team_id}`;
  return (
    <section aria-label={task.team} className="task">
      <h3>{task.team}</h3>
      <label>
        Assignee{" "}
        <select
          value={task.assignee_id ?? ""}
          disabled={closed}
          onChange={(event) => act(`${base}/assignee`, { user_id: event.target.value })}
        >
          <option value="" disabled>
            Unassigned
          </option>
          {team?.members.map((member) => (
            <option key={member.id} value={member.id}>
              {member.display_name}
              {member.is_lead ? " (lead)" : ""}
            </option>
          ))}
        </select>
      </label>
      <ul className="checklist">
        {task.checklist.map((item) => (
          <li key={item.id}>
            <label>
              <input
                type="checkbox"
                checked={item.done}
                disabled={closed}
                onChange={(event) =>
                  act(`/checklist/${item.id}`, { done: event.target.checked })
                }
              />{" "}
              {item.text}
            </label>
          </li>
        ))}
      </ul>
      {!closed && (
        <form
          onSubmit={(event) => {
            event.preventDefault();
            const form = event.currentTarget;
            act(`${base}/checklist`, { text: new FormData(form).get("text") }).then(() =>
              form.reset(),
            );
          }}
        >
          <input name="text" required maxLength={500} placeholder="New step" aria-label="New step" />{" "}
          <button type="submit">Add step</button>
        </form>
      )}
    </section>
  );
}
