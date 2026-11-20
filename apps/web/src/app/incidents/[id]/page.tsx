import { Suspense } from "react";
import { Incident } from "./incident";

// The id is only known at request time, so the client view waits inside a Suspense boundary.
export default function IncidentPage() {
  return (
    <Suspense fallback={<main className="shell wide status">Loading…</main>}>
      <Incident />
    </Suspense>
  );
}
