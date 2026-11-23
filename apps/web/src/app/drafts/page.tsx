"use client";

import { useRouter } from "next/navigation";
import { type FormEvent, useEffect, useId, useRef, useState } from "react";
import { getJson, postJson } from "@/lib/api";
import { type Draft, describe } from "@/lib/drafts";
import { SEVERITIES } from "@/lib/incidents";
import { useUserInvalid } from "@/lib/user-invalid";
import { AlertFigure } from "./alert-figure";

export default function DraftsPage() {
  const [drafts, setDrafts] = useState<Draft[] | null>(null);
  const [version, setVersion] = useState(0); // bumped after a dismissal to reload the list
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    getJson<Draft[]>("/drafts")
      .then(setDrafts)
      .catch((reason) => setError(String(reason)));
  }, [version]);

  return (
    <main className="shell wide">
      <h1>Alert drafts</h1>
      <p className="status">
        A firing alert waits here. Nobody is notified until it is raised as an incident.
      </p>
      {drafts && drafts.length > 0 && <p>Fields marked * are required.</p>}
      <p role="status">{status}</p>
      {error && <p role="alert">{error}</p>}
      {drafts?.length === 0 && <p className="status">No drafts waiting.</p>}
      {drafts?.map((draft) => (
        <DraftCard
          key={draft.id}
          draft={draft}
          onDismissed={() => {
            setStatus(`Dismissed the draft for ${draft.rule}.`);
            setVersion((v) => v + 1);
          }}
        />
      ))}
    </main>
  );
}

function DraftCard({ draft, onDismissed }: { draft: Draft; onDismissed: () => void }) {
  const router = useRouter();
  const form = useRef<HTMLFormElement>(null);
  const id = useId();
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);
  useUserInvalid(form);

  // Disabled only while a valid submission is in flight, so a second click cannot post twice.
  async function send(action: () => Promise<void>) {
    setPending(true);
    try {
      await action();
    } catch (reason) {
      setError(String(reason));
      setPending(false);
    }
  }

  function raise(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const body = Object.fromEntries(new FormData(event.currentTarget));
    send(async () => {
      const incident = await postJson<{ id: string }>(`/drafts/${draft.id}/raise`, body);
      router.push(`/incidents/${incident.id}`);
    });
  }

  const field = (name: string) => ({ id: `${id}-${name}`, name, "data-error": `${id}-${name}-error` });
  const required = (name: string, label: string) => (
    <p id={`${id}-${name}-error`} className="error-msg">
      <span role="img" aria-label="Error">
        ✖
      </span>{" "}
      {label} is required.
    </p>
  );

  return (
    <article className="task" aria-labelledby={`${id}-heading`}>
      <h2 id={`${id}-heading`}>
        {draft.rule} · {draft.service}
      </h2>
      <AlertFigure alert={draft} service={draft.service} />
      <form ref={form} className="stack" onSubmit={raise} aria-labelledby={`${id}-heading`}>
        <div className="field">
          <label htmlFor={`${id}-title`}>
            Title <span aria-hidden="true">*</span>
          </label>
          <input
            {...field("title")}
            required
            maxLength={200}
            defaultValue={`${draft.rule} on ${draft.service}`}
          />
          {required("title", "Title")}
        </div>
        <div className="field">
          <label htmlFor={`${id}-impact`}>
            Impact, as stakeholders will read it <span aria-hidden="true">*</span>
          </label>
          <textarea {...field("impact")} required maxLength={2000} rows={2} />
          {required("impact", "Impact")}
        </div>
        <div className="field">
          <label htmlFor={`${id}-description`}>
            Description <span aria-hidden="true">*</span>
          </label>
          <textarea
            {...field("description")}
            required
            maxLength={10000}
            rows={3}
            defaultValue={describe(draft, draft.service)}
          />
          {required("description", "Description")}
        </div>
        <div className="field">
          <label htmlFor={`${id}-severity`}>Severity</label>
          <select id={`${id}-severity`} name="severity" defaultValue={draft.severity}>
            {SEVERITIES.map((severity) => (
              <option key={severity}>{severity}</option>
            ))}
          </select>
        </div>
        <div className="filters">
          <button type="submit" disabled={pending}>
            Raise incident<span className="visually-hidden"> for {draft.rule}</span>
          </button>
          <button
            type="button"
            disabled={pending}
            onClick={() =>
              send(async () => {
                await postJson(`/drafts/${draft.id}/dismiss`, {});
                onDismissed();
              })
            }
          >
            Dismiss<span className="visually-hidden"> the draft for {draft.rule}</span>
          </button>
        </div>
      </form>
      {error && <p role="alert">{error}</p>}
    </article>
  );
}
