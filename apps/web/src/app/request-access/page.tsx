"use client";

import { type FormEvent, useState } from "react";
import { postJson } from "@/lib/api";

export default function RequestAccessPage() {
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      await postJson("/access-requests", {
        display_name: String(form.get("display_name")),
        email: String(form.get("email")),
      });
      setSent(true);
    } catch (reason) {
      setError(String(reason));
    }
  }

  return (
    <main className="shell">
      <h1>Request access</h1>
      {sent ? (
        <p role="status">Request sent. An administrator will review it.</p>
      ) : (
        <form className="filters" onSubmit={submit}>
          <label>
            Name <input name="display_name" required maxLength={100} />
          </label>
          <label>
            Email <input type="email" name="email" required maxLength={254} />
          </label>
          <button type="submit">Send request</button>
        </form>
      )}
      {error && <p role="alert">{error}</p>}
    </main>
  );
}
