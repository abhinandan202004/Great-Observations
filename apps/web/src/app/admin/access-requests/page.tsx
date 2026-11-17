"use client";

import { type FormEvent, useEffect, useState } from "react";
import { getJson, postJson } from "@/lib/api";

const ROLES = [
  "production_support",
  "developer",
  "sre",
  "admin",
  "incident_commander",
  "comms",
  "viewer",
  "stakeholder",
];

type Pending = { id: string; email: string; display_name: string; requested_at: string };

export default function AccessRequestsPage() {
  const [pending, setPending] = useState<Pending[] | null>(null);
  const [version, setVersion] = useState(0); // bumped after each decision to reload the list
  const [error, setError] = useState("");

  useEffect(() => {
    getJson<Pending[]>("/access-requests")
      .then(setPending)
      .catch((reason) => setError(String(reason)));
  }, [version]);

  return (
    <main className="shell wide">
      <h1>Access requests</h1>
      {error && <p role="alert">{error}</p>}
      {pending?.length === 0 && <p className="status">No pending requests.</p>}
      {pending && pending.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Requested</th>
              <th>Decide</th>
            </tr>
          </thead>
          <tbody>
            {pending.map((request) => (
              <Decision
                key={request.id}
                request={request}
                onDecided={() => setVersion((v) => v + 1)}
              />
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}

function Decision({ request, onDecided }: { request: Pending; onDecided: () => void }) {
  const [error, setError] = useState("");

  async function approve(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      await postJson(`/access-requests/${request.id}/approve`, {
        role: String(form.get("role")),
        password: String(form.get("password")),
      });
      onDecided();
    } catch (reason) {
      setError(String(reason));
    }
  }

  async function reject() {
    try {
      await postJson(`/access-requests/${request.id}/reject`, {});
      onDecided();
    } catch (reason) {
      setError(String(reason));
    }
  }

  return (
    <tr>
      <td>{request.display_name}</td>
      <td>{request.email}</td>
      <td>{new Date(request.requested_at).toLocaleString()}</td>
      <td>
        <form onSubmit={approve}>
          <label>
            Role{" "}
            <select name="role" defaultValue="viewer">
              {ROLES.map((role) => (
                <option key={role}>{role}</option>
              ))}
            </select>
          </label>{" "}
          <label>
            Temporary password{" "}
            <input type="password" name="password" required minLength={12} />
          </label>{" "}
          <button type="submit">Approve</button>{" "}
          <button type="button" onClick={reject}>
            Reject
          </button>
        </form>
        {error && <p role="alert">{error}</p>}
      </td>
    </tr>
  );
}
