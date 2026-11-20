"use client";

import { useRouter } from "next/navigation";
import { type FormEvent, useEffect, useState } from "react";
import { getJson, postJson } from "@/lib/api";
import { type Detail, SEVERITIES } from "@/lib/incidents";

export default function RaiseIncidentPage() {
  const router = useRouter();
  const [services, setServices] = useState<string[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getJson<string[]>("/services")
      .then(setServices)
      .catch((reason) => setError(String(reason)));
  }, []);

  async function raise(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = Object.fromEntries(new FormData(event.currentTarget));
    try {
      const incident = await postJson<Detail>("/incidents", form);
      router.push(`/incidents/${incident.id}`);
    } catch (reason) {
      setError(String(reason));
    }
  }

  return (
    <main className="shell">
      <h1>Raise an incident</h1>
      <form className="stack" onSubmit={raise}>
        <label>
          Title <input name="title" required maxLength={200} />
        </label>
        <label>
          Impact, as stakeholders will read it{" "}
          <textarea name="impact" required maxLength={2000} rows={2} />
        </label>
        <label>
          Description <textarea name="description" required maxLength={10000} rows={5} />
        </label>
        <label>
          Severity{" "}
          <select name="severity" defaultValue="P3">
            {SEVERITIES.map((severity) => (
              <option key={severity}>{severity}</option>
            ))}
          </select>
        </label>
        <label>
          Service{" "}
          <select name="service" required>
            {services.map((name) => (
              <option key={name}>{name}</option>
            ))}
          </select>
        </label>
        <button type="submit">Raise</button>
      </form>
      {error && <p role="alert">{error}</p>}
    </main>
  );
}
