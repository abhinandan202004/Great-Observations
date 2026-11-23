"use client";

import Link from "next/link";
import { type FormEvent, useCallback, useEffect, useId, useRef, useState } from "react";
import { getJson, postJson } from "@/lib/api";
import type { Status, Summary } from "@/lib/incidents";
import { CATEGORIES, type Category, type Runbook, type Version } from "@/lib/runbooks";
import { useUserInvalid } from "@/lib/user-invalid";

const TEXT_FIELDS = [
  ["timeline", "Timeline", "Detection, acknowledgement, mitigation and resolution times, and key events."],
  ["root_cause", "Root cause", "What went wrong, in detail."],
  ["contributing_factors", "Contributing factors", "What slowed detection or recovery, or made the impact larger."],
  ["remediation", "Remediation and prevention", "What fixed it, and the follow-ups that stop it happening again."],
  ["workaround", "Workaround applied", "Any temporary measure, and whether it is still in place."],
] as const;

export function RunbookPanel({ incidentId, status }: { incidentId: string; status: Status }) {
  const base = `/incidents/${incidentId}/runbook`;
  const [runbook, setRunbook] = useState<Runbook | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const reload = useCallback(
    () =>
      getJson<Runbook>(base)
        .then(setRunbook)
        .catch((reason) => setError(String(reason))),
    [base],
  );
  useEffect(() => {
    reload();
  }, [reload, status]);

  // Every action reports through here: one status message, one error, then a fresh runbook.
  const done = (what: string) => async (action: Promise<unknown>) => {
    try {
      await action;
      setError("");
      setMessage(what);
      await reload();
      return true;
    } catch (reason) {
      setError(String(reason));
      return false;
    }
  };

  if (!runbook || (status !== "resolved" && runbook.versions.length === 0)) return null;
  const latest = runbook.versions.at(-1);
  const canWrite = status === "resolved" && runbook.pending_version === null && !runbook.may_close;
  return (
    <section aria-labelledby="runbook-heading" className="runbook">
      <h2 id="runbook-heading">Runbook</h2>
      <p>
        {runbook.may_close
          ? "Approved for this resolution: the caller can now close the incident."
          : status === "resolved"
            ? "The caller can close the incident once a runbook version is approved."
            : null}
      </p>
      <p role="status">{message}</p>
      {error && <p role="alert">{error}</p>}
      {runbook.pending_version !== null && (
        <ReviewForm base={base} version={runbook.pending_version} done={done} />
      )}
      {canWrite && (
        <RunbookForm
          base={base}
          incidentId={incidentId}
          suggested={runbook.suggested_timeline}
          returned={latest?.review?.decision === "returned" ? latest : undefined}
          done={done}
        />
      )}
      {[...runbook.versions].reverse().map((version, index) =>
        index === 0 ? (
          <VersionView key={version.version} version={version} />
        ) : (
          <details key={version.version}>
            <summary>
              Version {version.version} by {version.author}
              {version.review ? `, ${version.review.decision}` : ""}
            </summary>
            <VersionView version={version} />
          </details>
        ),
      )}
    </section>
  );
}

type Done = (what: string) => (action: Promise<unknown>) => Promise<boolean>;

function VersionView({ version: v }: { version: Version }) {
  return (
    <article aria-label={`Runbook version ${v.version}`} className="task">
      <h3>
        Version {v.version} by {v.author},{" "}
        <time dateTime={v.created_at}>{new Date(v.created_at).toLocaleString()}</time>
      </h3>
      <p>
        {v.review ? (
          <>
            <strong>{v.review.decision === "approved" ? "Approved" : "Returned"}</strong> by{" "}
            {v.review.reviewer}
            {v.review.comment && `: ${v.review.comment}`}
          </>
        ) : (
          <strong>Waiting for review</strong>
        )}
      </p>
      <dl className="runbook-fields">
        <div>
          <dt>Root cause category</dt>
          <dd>{CATEGORIES[v.root_cause_category]}</dd>
        </div>
        {TEXT_FIELDS.map(([name, label]) => (
          <div key={name}>
            <dt>{label}</dt>
            <dd className="prose">{v[name]}</dd>
          </div>
        ))}
        <div>
          <dt>Similar incidents</dt>
          <dd>
          {v.similar_incidents.length > 0 ? (
            <ul>
              {v.similar_incidents.map((s) => (
                <li key={s.id}>
                  <Link href={`/incidents/${s.id}`}>
                    #{s.number} {s.title}
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <span className="prose">None found. {v.none_similar}</span>
          )}
          </dd>
        </div>
      </dl>
    </article>
  );
}

function RunbookForm(props: {
  base: string;
  incidentId: string;
  suggested: string;
  returned?: Version;
  done: Done;
}) {
  const id = useId();
  const form = useRef<HTMLFormElement>(null);
  useUserInvalid(form);
  const [incidents, setIncidents] = useState<Summary[]>([]);
  const start = props.returned;

  useEffect(() => {
    getJson<Summary[]>("/incidents")
      .then((all) => setIncidents(all.filter((i) => i.id !== props.incidentId)))
      .catch(() => setIncidents([]));
  }, [props.incidentId]);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const fields = new FormData(event.currentTarget);
    const text = (name: string) => String(fields.get(name) ?? "");
    props.done("Runbook submitted for review.")(
      postJson(props.base, {
        ...Object.fromEntries(TEXT_FIELDS.map(([name]) => [name, text(name)])),
        root_cause_category: text("root_cause_category"),
        similar_incident_ids: fields.getAll("similar"),
        none_similar: text("none_similar"),
      }),
    );
  }

  return (
    <form ref={form} className="stack task" onSubmit={submit} aria-labelledby={`${id}-heading`}>
      <h3 id={`${id}-heading`}>
        {start ? `Revise version ${start.version}` : "Write the runbook"}
      </h3>
      <p>Fields marked * are required. The server checks every one before accepting it.</p>
      <div className="field">
        <label htmlFor={`${id}-category`}>
          Root cause category <span aria-hidden="true">*</span>
        </label>
        <select
          id={`${id}-category`}
          name="root_cause_category"
          required
          defaultValue={start?.root_cause_category ?? ""}
          data-error={`${id}-category-error`}
        >
          <option value="" disabled>
            Choose a category
          </option>
          {(Object.entries(CATEGORIES) as [Category, string][]).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        <p id={`${id}-category-error`} className="error-msg">
          <span role="img" aria-label="Error">
            ✖
          </span>{" "}
          Choose a root cause category.
        </p>
      </div>
      {TEXT_FIELDS.map(([name, label, hint]) => (
        <div className="field" key={name}>
          <label htmlFor={`${id}-${name}`}>
            {label} <span aria-hidden="true">*</span>
          </label>
          <span id={`${id}-${name}-hint`} className="status">
            {hint}
          </span>
          <textarea
            id={`${id}-${name}`}
            name={name}
            required
            maxLength={name === "timeline" ? 20000 : 10000}
            aria-describedby={`${id}-${name}-hint`}
            data-error={`${id}-${name}-error`}
            defaultValue={start?.[name] ?? (name === "timeline" ? props.suggested : "")}
          />
          <p id={`${id}-${name}-error`} className="error-msg">
            <span role="img" aria-label="Error">
              ✖
            </span>{" "}
            {label} is required.
          </p>
        </div>
      ))}
      <fieldset className="log-picker">
        <legend>
          Similar incidents <span aria-hidden="true">*</span>
        </legend>
        <p className="status">Tick any that are similar, or say below that none were found.</p>
        {incidents.map((incident) => (
          <div key={incident.id}>
            <input
              type="checkbox"
              id={`${id}-similar-${incident.id}`}
              name="similar"
              value={incident.id}
              defaultChecked={start?.similar_incidents.some((s) => s.id === incident.id)}
            />
            <label htmlFor={`${id}-similar-${incident.id}`}>
              #{incident.number} {incident.title} ({incident.service})
            </label>
          </div>
        ))}
      </fieldset>
      <div className="field">
        <label htmlFor={`${id}-none`}>If none are similar: what did you search?</label>
        <textarea
          id={`${id}-none`}
          name="none_similar"
          maxLength={2000}
          defaultValue={start?.none_similar ?? ""}
        />
      </div>
      <button type="submit">Submit for review</button>
    </form>
  );
}

function ReviewForm({ base, version, done }: { base: string; version: number; done: Done }) {
  const id = useId();
  const form = useRef<HTMLFormElement>(null);
  useUserInvalid(form);

  function review(decision: "approved" | "returned", comment = "") {
    return done(`Version ${version} ${decision}.`)(
      postJson(`${base}/${version}/review`, { decision, comment }),
    );
  }

  return (
    <div className="task">
      <h3>Version {version} waits for review</h3>
      <p className="status">
        The Incident Commander or a lead of a team on this incident reviews it, never its author.
      </p>
      <button type="button" onClick={() => review("approved")}>
        Approve version {version}
      </button>
      <form
        ref={form}
        className="stack"
        aria-labelledby={`${id}-heading`}
        onSubmit={(event) => {
          event.preventDefault();
          review("returned", String(new FormData(event.currentTarget).get("comment") ?? ""));
        }}
      >
        <h4 id={`${id}-heading`}>Or return it</h4>
        <div className="field">
          <label htmlFor={`${id}-comment`}>
            What should change <span aria-hidden="true">*</span>
          </label>
          <textarea
            id={`${id}-comment`}
            name="comment"
            required
            maxLength={5000}
            data-error={`${id}-comment-error`}
          />
          <p id={`${id}-comment-error`} className="error-msg">
            <span role="img" aria-label="Error">
              ✖
            </span>{" "}
            Say what should change.
          </p>
        </div>
        <button type="submit">Return version {version}</button>
      </form>
    </div>
  );
}
