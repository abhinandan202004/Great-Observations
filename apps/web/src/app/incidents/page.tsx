"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getJson } from "@/lib/api";
import type { Summary } from "@/lib/incidents";
import { Clock } from "./clock";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Summary[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getJson<Summary[]>("/incidents")
      .then(setIncidents)
      .catch((reason) => setError(String(reason)));
  }, []);

  return (
    <main className="shell wide">
      <h1>Incidents</h1>
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
