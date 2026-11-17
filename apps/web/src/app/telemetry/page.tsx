"use client";

import { useEffect, useState } from "react";
import { formatTime, getJson } from "@/lib/api";
import { Chart, type Change, type Point } from "./chart";

const POLL_MS = 5000;

export default function TelemetryPage() {
  const [services, setServices] = useState<string[]>([]);
  const [service, setService] = useState("");
  const [minutes, setMinutes] = useState(15);
  const [series, setSeries] = useState<Record<string, Point[]>>({});
  const [changes, setChanges] = useState<Change[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getJson<string[]>("/services")
      .then((names) => {
        setServices(names);
        setService(names[0] ?? "");
      })
      .catch((reason) => setError(String(reason)));
  }, []);

  useEffect(() => {
    if (!service) return;
    let stale = false;
    async function load() {
      const since = new Date(Date.now() - minutes * 60_000).toISOString();
      const base = `/services/${encodeURIComponent(service)}`;
      try {
        const [names, marks] = await Promise.all([
          getJson<string[]>(`${base}/metrics?since=${since}`),
          getJson<Change[]>(`${base}/changes?since=${since}`),
        ]);
        const points = await Promise.all(
          names.map((name) =>
            getJson<Point[]>(
              `${base}/metrics/${encodeURIComponent(name)}?since=${since}`,
            ),
          ),
        );
        if (stale) return;
        setSeries(Object.fromEntries(names.map((name, i) => [name, points[i]])));
        setChanges(marks);
        setError("");
      } catch (reason) {
        if (!stale) setError(String(reason));
      }
    }
    load();
    const timer = setInterval(load, POLL_MS);
    return () => {
      stale = true;
      clearInterval(timer);
    };
  }, [service, minutes]);

  return (
    <main className="shell wide">
      <h1>Telemetry</h1>
      <div className="filters">
        <label>
          Service{" "}
          <select
            value={service}
            onChange={(event) => {
              setSeries({});
              setChanges([]);
              setService(event.target.value);
            }}
          >
            {services.map((name) => (
              <option key={name}>{name}</option>
            ))}
          </select>
        </label>
        <label>
          Time range{" "}
          <select
            value={minutes}
            onChange={(event) => setMinutes(Number(event.target.value))}
          >
            <option value={15}>Last 15 minutes</option>
            <option value={60}>Last hour</option>
          </select>
        </label>
      </div>
      {error && <p role="alert">{error}</p>}
      {service && Object.keys(series).length === 0 && !error && (
        <p className="status">No metrics from {service} in this time range.</p>
      )}
      {Object.entries(series).map(([metric, points]) => (
        <section key={metric}>
          <h2>{metric}</h2>
          <Chart
            label={`${metric} for ${service}, latest value ${points.at(-1)?.value.toFixed(2) ?? "none"}`}
            points={points}
            changes={changes}
          />
        </section>
      ))}
      <h2>Changes</h2>
      {changes.length === 0 ? (
        <p className="status">No deploys, config or feature-flag changes.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Kind</th>
              <th>Summary</th>
            </tr>
          </thead>
          <tbody>
            {changes.map((change) => (
              <tr key={change.time + change.summary}>
                <td>{formatTime(change.time)}</td>
                <td>{change.kind}</td>
                <td>{change.summary}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}
