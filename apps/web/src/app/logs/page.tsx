"use client";

import { type FormEvent, useEffect, useState } from "react";
import { getJson } from "@/lib/api";

type LogLine = {
  time: string;
  service: string;
  level: string;
  message: string;
  correlation_id: string | null;
};

const LEVELS = ["debug", "info", "warning", "error"];

export default function LogsPage() {
  const [services, setServices] = useState<string[]>([]);
  const [lines, setLines] = useState<LogLine[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getJson<string[]>("/services")
      .then(setServices)
      .catch((reason) => setError(String(reason)));
  }, []);

  async function search(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const query = new URLSearchParams();
    for (const name of ["service", "level", "q"]) {
      const value = String(form.get(name) ?? "").trim();
      if (value) query.set(name, value);
    }
    // The inputs hold local time; the API needs a time zone.
    const since = String(form.get("since") ?? "");
    const until = String(form.get("until") ?? "");
    query.set(
      "since",
      (since ? new Date(since) : new Date(Date.now() - 15 * 60_000)).toISOString(),
    );
    if (until) query.set("until", new Date(until).toISOString());
    try {
      setLines(await getJson<LogLine[]>(`/logs?${query}`));
      setError("");
    } catch (reason) {
      setError(String(reason));
    }
  }

  return (
    <main className="shell wide">
      <h1>Logs</h1>
      <form className="filters" onSubmit={search}>
        <label>
          Service{" "}
          <select name="service">
            <option value="">All</option>
            {services.map((name) => (
              <option key={name}>{name}</option>
            ))}
          </select>
        </label>
        <label>
          Level{" "}
          <select name="level">
            <option value="">All</option>
            {LEVELS.map((level) => (
              <option key={level}>{level}</option>
            ))}
          </select>
        </label>
        <label>
          From <input type="datetime-local" name="since" />
        </label>
        <label>
          To <input type="datetime-local" name="until" />
        </label>
        <label>
          Text or correlation ID <input type="search" name="q" maxLength={200} />
        </label>
        <button type="submit">Search</button>
      </form>
      <p className="status">
        Leave “From” empty to search the last 15 minutes. Newest first, at most
        200 entries.
      </p>
      {error && <p role="alert">{error}</p>}
      {lines?.length === 0 && <p>No log entries match.</p>}
      {lines && lines.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Service</th>
              <th>Level</th>
              <th>Message</th>
              <th>Correlation ID</th>
            </tr>
          </thead>
          <tbody>
            {lines.map((line, index) => (
              <tr key={index}>
                <td>{new Date(line.time).toLocaleString()}</td>
                <td>{line.service}</td>
                <td>{line.level}</td>
                <td>{line.message}</td>
                <td>
                  <code>{line.correlation_id}</code>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}
