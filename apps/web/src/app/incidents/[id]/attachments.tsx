"use client";

import { type FormEvent, useCallback, useEffect, useId, useRef, useState } from "react";
import { getBlob, getJson, postJson, upload } from "@/lib/api";
import {
  ACCEPTED_FILES,
  type Attachment,
  formatBytes,
  type LogLine,
  MAX_FILE_BYTES,
  saveFile,
} from "@/lib/attachments";
import { useUserInvalid } from "@/lib/user-invalid";
import { PointsFigure } from "../../drafts/alert-figure";

const RANGES = [15, 30, 60];

export function Attachments(props: {
  incidentId: string;
  service: string;
  raisedAt: string;
  open: boolean;
  version: number; // goes up when the incident changed elsewhere
}) {
  const base = `/incidents/${props.incidentId}/attachments`;
  const [list, setList] = useState<Attachment[] | null>(null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  const reload = useCallback(
    () =>
      getJson<Attachment[]>(base)
        .then(setList)
        .catch((reason) => setError(String(reason))),
    [base],
  );
  useEffect(() => {
    reload();
  }, [reload, props.version]);

  // Every form reports through here: one status message, one error, then a fresh list.
  const added = (what: string) => async (action: Promise<unknown>) => {
    try {
      await action;
      setError("");
      setStatus(`Attached ${what}.`);
      await reload();
      return true;
    } catch (reason) {
      setError(String(reason));
      return false;
    }
  };

  return (
    <section aria-labelledby="attachments-heading">
      <h2 id="attachments-heading">Attachments</h2>
      {list?.length === 0 && <p className="status">Nothing attached yet.</p>}
      {list && list.length > 0 && (
        <ul className="attachments">
          {list.map((attachment) => (
            <li key={attachment.id}>
              <AttachmentView attachment={attachment} onError={setError} />
            </li>
          ))}
        </ul>
      )}
      <p role="status">{status}</p>
      {error && <p role="alert">{error}</p>}
      {props.open && (
        <>
          <NoteForm base={base} added={added} />
          <SnapshotForm base={base} service={props.service} added={added} />
          <LogForm base={base} {...props} added={added} />
          <FileForm base={base} added={added} onError={setError} />
        </>
      )}
    </section>
  );
}

type Added = (what: string) => (action: Promise<unknown>) => Promise<boolean>;

function AttachmentView({
  attachment: a,
  onError,
}: {
  attachment: Attachment;
  onError: (message: string) => void;
}) {
  const by = (
    <p className="status">
      {a.created_by}, <time dateTime={a.created_at}>{new Date(a.created_at).toLocaleString()}</time>
    </p>
  );
  switch (a.kind) {
    case "metric_snapshot":
      return (
        <article aria-label={a.title}>
          <h3>{a.title}</h3>
          <PointsFigure
            label={`${a.data.metric} on ${a.data.service}, frozen when attached`}
            caption={`${a.data.points.length} samples from ${new Date(a.data.since).toLocaleString()} to ${new Date(a.data.until).toLocaleString()}.`}
            points={a.data.points}
          />
          {by}
        </article>
      );
    case "log_excerpt":
      return (
        <article aria-label={a.title}>
          <h3>{a.title}</h3>
          <table>
            <caption>Log lines as they were when attached</caption>
            <thead>
              <tr>
                <th scope="col">Time</th>
                <th scope="col">Level</th>
                <th scope="col">Message</th>
                <th scope="col">Correlation id</th>
              </tr>
            </thead>
            <tbody>
              {a.data.lines.map((line, index) => (
                <tr key={`${line.time}-${index}`}>
                  <td>
                    <time dateTime={line.time}>{new Date(line.time).toLocaleTimeString()}</time>
                  </td>
                  <td>{line.level}</td>
                  <td>{line.message}</td>
                  <td>{line.correlation_id}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {by}
        </article>
      );
    case "link":
    case "note":
      return (
        <article aria-label={a.title}>
          {a.data.url ? (
            // The API accepts only http(s) links, so this can never be a javascript: URL.
            <a href={a.data.url} rel="noopener noreferrer">
              {a.title}
            </a>
          ) : null}
          <p className="prose">{a.data.text}</p>
          {by}
        </article>
      );
    case "file":
      return (
        <article aria-label={a.title}>
          <span className="file-name">{a.file_name}</span>{" "}
          <span className="status">
            {a.content_type?.split(";")[0]}, {formatBytes(a.size_bytes ?? 0)}
          </span>{" "}
          <button
            type="button"
            onClick={() =>
              // A plain link cannot send the sign-in token, so the bytes are fetched first.
              getBlob(`/attachments/${a.id}/file`)
                .then((blob) => saveFile(blob, a.file_name ?? "file"))
                .catch((reason) => onError(String(reason)))
            }
            aria-label={`Download ${a.file_name}`}
          >
            Download
          </button>
          {by}
        </article>
      );
  }
}

function NoteForm({ base, added }: { base: string; added: Added }) {
  const id = useId();
  const form = useRef<HTMLFormElement>(null);
  useUserInvalid(form);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const target = event.currentTarget;
    const fields = new FormData(target);
    const url = String(fields.get("url") ?? "").trim();
    const ok = await added(url ? "the link" : "the note")(
      postJson(`${base}/note`, { text: fields.get("text"), url: url || null }),
    );
    if (ok) target.reset();
  }

  return (
    <form ref={form} className="stack task" onSubmit={submit} aria-labelledby={`${id}-heading`}>
      <h3 id={`${id}-heading`}>Add a note or link</h3>
      <div className="field">
        <label htmlFor={`${id}-text`}>
          Note <span aria-hidden="true">*</span>
        </label>
        <textarea
          id={`${id}-text`}
          name="text"
          required
          maxLength={5000}
          rows={3}
          data-error={`${id}-text-error`}
        />
        <p id={`${id}-text-error`} className="error-msg">
          <span role="img" aria-label="Error">
            ✖
          </span>{" "}
          A note is required.
        </p>
      </div>
      <div className="field">
        <label htmlFor={`${id}-url`}>Link (optional)</label>
        <span id={`${id}-url-hint`} className="status">
          An http or https address, for example a dashboard or a ticket.
        </span>
        <input
          id={`${id}-url`}
          name="url"
          type="url"
          inputMode="url"
          autoComplete="off"
          spellCheck={false}
          aria-describedby={`${id}-url-hint`}
        />
      </div>
      <button type="submit">Add</button>
    </form>
  );
}

function SnapshotForm({ base, service, added }: { base: string; service: string; added: Added }) {
  const id = useId();
  const [metrics, setMetrics] = useState<string[]>([]);

  useEffect(() => {
    getJson<string[]>(`/services/${service}/metrics`)
      .then(setMetrics)
      .catch(() => setMetrics([]));
  }, [service]);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const fields = new FormData(event.currentTarget);
    const until = new Date();
    const since = new Date(until.getTime() - Number(fields.get("minutes")) * 60_000);
    added("the metric snapshot")(
      postJson(`${base}/snapshot`, {
        service,
        metric: fields.get("metric"),
        since: since.toISOString(),
        until: until.toISOString(),
      }),
    );
  }

  return (
    <form className="filters task" onSubmit={submit} aria-labelledby={`${id}-heading`}>
      <h3 id={`${id}-heading`}>Attach a metric snapshot</h3>
      <div className="field">
        <label htmlFor={`${id}-metric`}>Metric on {service}</label>
        <select id={`${id}-metric`} name="metric" required>
          {metrics.map((metric) => (
            <option key={metric}>{metric}</option>
          ))}
        </select>
      </div>
      <div className="field">
        <label htmlFor={`${id}-minutes`}>Period</label>
        <select id={`${id}-minutes`} name="minutes" defaultValue={30}>
          {RANGES.map((minutes) => (
            <option key={minutes} value={minutes}>
              Last {minutes} minutes
            </option>
          ))}
        </select>
      </div>
      <button type="submit" disabled={metrics.length === 0}>
        Attach snapshot
      </button>
    </form>
  );
}

function LogForm(props: { base: string; service: string; raisedAt: string; added: Added }) {
  const id = useId();
  const [lines, setLines] = useState<LogLine[]>([]);

  useEffect(() => {
    // The half hour before the raise, up to now, where the evidence usually is.
    const since = new Date(Date.parse(props.raisedAt) - 30 * 60_000).toISOString();
    const query = new URLSearchParams({ service: props.service, since, limit: "50" });
    getJson<LogLine[]>(`/logs?${query}`)
      .then(setLines)
      .catch(() => setLines([]));
  }, [props.service, props.raisedAt]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const target = event.currentTarget;
    const ids = new FormData(target).getAll("line");
    if (ids.length === 0) return;
    if (await props.added(`${ids.length} log lines`)(postJson(`${props.base}/logs`, { ids }))) {
      target.reset();
    }
  }

  if (lines.length === 0) return null;
  return (
    <form className="task" onSubmit={submit} aria-labelledby={`${id}-heading`}>
      <h3 id={`${id}-heading`}>Attach log lines</h3>
      <fieldset className="log-picker">
        <legend>Recent {props.service} log lines</legend>
        {lines.map((line) => (
          <div key={line.id}>
            <input type="checkbox" id={`${id}-${line.id}`} name="line" value={line.id} />
            <label htmlFor={`${id}-${line.id}`}>
              <time dateTime={line.time}>{new Date(line.time).toLocaleTimeString()}</time>{" "}
              {line.level} {line.message}
            </label>
          </div>
        ))}
      </fieldset>
      <button type="submit">Attach selected lines</button>
    </form>
  );
}

function FileForm(props: { base: string; added: Added; onError: (message: string) => void }) {
  const id = useId();
  const [progress, setProgress] = useState<number | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const target = event.currentTarget;
    const file = (new FormData(target).get("file") as File | null) ?? null;
    if (!file || file.size === 0) return;
    if (file.size > MAX_FILE_BYTES) {
      props.onError(`${file.name} is ${formatBytes(file.size)}; files may be at most 10 MB.`);
      return;
    }
    setProgress(0);
    const ok = await props.added(file.name)(
      upload(`${props.base}/file?${new URLSearchParams({ name: file.name })}`, file, (sent, total) =>
        setProgress(sent / total),
      ),
    );
    setProgress(null);
    if (ok) target.reset();
  }

  return (
    <form className="filters task" onSubmit={submit} aria-labelledby={`${id}-heading`}>
      <h3 id={`${id}-heading`}>Attach a file or screenshot</h3>
      <div className="field">
        <label htmlFor={`${id}-file`}>File</label>
        <span id={`${id}-file-hint`} className="status">
          PNG, JPEG, GIF, WebP, PDF, or a .txt or .log file, up to 10 MB.
        </span>
        <input
          id={`${id}-file`}
          name="file"
          type="file"
          accept={ACCEPTED_FILES}
          required
          aria-describedby={`${id}-file-hint`}
        />
      </div>
      <button type="submit" disabled={progress !== null}>
        Upload
      </button>
      {progress !== null && (
        <div className="field">
          <label htmlFor={`${id}-progress`}>Uploading</label>
          <progress id={`${id}-progress`} max={1} value={progress} />
        </div>
      )}
    </form>
  );
}
