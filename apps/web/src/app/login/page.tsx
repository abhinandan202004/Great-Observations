"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { type FormEvent, useState } from "react";
import { signIn } from "@/lib/session";

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    if (await signIn(String(form.get("email")), String(form.get("password")))) {
      router.push("/");
    } else {
      setError("Wrong email or password.");
    }
  }

  return (
    <main className="shell">
      <h1>Sign in</h1>
      <form className="filters" onSubmit={submit}>
        <label>
          Email <input type="email" name="email" required />
        </label>
        <label>
          Password <input type="password" name="password" required />
        </label>
        <button type="submit">Sign in</button>
      </form>
      {error && <p role="alert">{error}</p>}
      <p className="status">
        No account yet? <Link href="/request-access">Request access</Link>.
      </p>
    </main>
  );
}
