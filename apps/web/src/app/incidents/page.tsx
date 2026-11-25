"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { LiveStatus } from "../live-status";
import { getJson } from "@/lib/api";
import { ALL, useLive } from "@/lib/live";
import type { Summary } from "@/lib/incidents";
import { Clock } from "./clock";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Summary[] | null>(null);
  const [error, setError] = useState("");
  const { live, version, notice } = useLive(ALL);

  useEffect(() => {
    let latest = true; // a slower, older answer must not overwrite a newer one
    getJson<Summary[]>("/incidents")
      .then((found) => latest && setIncidents(found))
      .catch((reason) => latest && setError(String(reason)));
    return () => {
      latest = false;
    };
  }, [version]);

  return (
    <main className="shell wide">
      <h1>Incidents</h1>
      <LiveStatus live={live} notice={notice} />
      <p>
        <Link href="/incidents/new">Raise an incident</Link>
      </p>
      {error && <p role="alert">{error}</p>}
      {incidents?.length === 0 && <p className="status">No incidents.</p>}
      {incidents && incidents.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Title</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Service</th>
              <th>Acknowledge</th>
              <th>Resolve</th>
            </tr>
          </thead>
          <tbody>
            {incidents.map((incident) => (
              <tr key={incident.id}>
                <td>{incident.number}</td>
                <td>
                  <Link href={`/incidents/${incident.id}`}>{incident.title}</Link>
                </td>
                <td>{incident.severity}</td>
                <td>{incident.status}</td>
                <td>{incident.service}</td>
                <td>
                  <Clock timer={incident.acknowledge} />
                </td>
                <td>
                  <Clock timer={incident.resolve} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}
