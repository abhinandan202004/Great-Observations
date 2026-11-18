"use client";

import { type FormEvent, useEffect, useState } from "react";
import { getJson, putJson } from "@/lib/api";

type Policy = { severity: string; acknowledge_minutes: number; resolve_minutes: number };

export default function SlaPolicyPage() {
  const [policies, setPolicies] = useState<Policy[] | null>(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    getJson<Policy[]>("/sla-policies")
      .then(setPolicies)
      .catch((reason) => setMessage(String(reason)));
  }, []);

  async function save(event: FormEvent<HTMLFormElement>, severity: string) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      const saved = await putJson<Policy>(`/sla-policies/${severity}`, {
        acknowledge_minutes: Number(form.get("acknowledge_minutes")),
        resolve_minutes: Number(form.get("resolve_minutes")),
      });
      setPolicies((all) => all?.map((p) => (p.severity === severity ? saved : p)) ?? null);
      setMessage(`Saved the ${severity} policy.`);
    } catch (reason) {
      setMessage(String(reason));
    }
  }

  return (
    <main className="shell wide">
      <h1>SLA policy</h1>
      {message && <p role="status">{message}</p>}
      {policies?.map((policy) => (
        <form key={policy.severity} className="filters" onSubmit={(e) => save(e, policy.severity)}>
          <strong>{policy.severity}</strong>
          <label>
            Acknowledge within (minutes){" "}
            <input
              name="acknowledge_minutes"
              type="number"
              min={1}
              required
              defaultValue={policy.acknowledge_minutes}
            />
          </label>
          <label>
            Resolve within (minutes){" "}
            <input
              name="resolve_minutes"
              type="number"
              min={1}
              required
              defaultValue={policy.resolve_minutes}
            />
          </label>
          <button type="submit">Save</button>
        </form>
      ))}
    </main>
  );
}
