"use client";

import { useEffect, useState } from "react";
import { type SlaTimer, timerText } from "@/lib/incidents";

/** An SLA timer that keeps counting between fetches. A breach is labelled, not only coloured. */
export function Clock({ timer }: { timer: SlaTimer }) {
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    if (timer.stopped_at !== null) return;
    const tick = setInterval(() => setNow(Date.now()), 15_000);
    return () => clearInterval(tick);
  }, [timer.stopped_at]);

  const { text, breached } = timerText(timer, now);
  return (
    <span className={breached ? "breach" : undefined}>
      {breached && <strong>Breached: </strong>}
      {text}
    </span>
  );
}
