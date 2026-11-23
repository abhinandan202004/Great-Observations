import type { Point } from "@/app/telemetry/chart";

/** An alert and the metric points frozen when it first fired. */
export type FiredAlert = {
  rule: string;
  metric: string;
  comparator: "above" | "below";
  threshold: number;
  breach_started_at: string;
  last_fired_at: string;
  fire_count: number;
  snapshot: Point[];
};

export type Draft = FiredAlert & { id: string; service: string; severity: string };

/** What the alert saw, in words, so it reads the same without the chart. */
export function describe(alert: FiredAlert, service: string): string {
  const since = new Date(alert.breach_started_at).toLocaleString();
  const latest = alert.snapshot.at(-1)?.value;
  const times = alert.fire_count === 1 ? "once" : `${alert.fire_count} times`;
  return (
    `${alert.metric} on ${service} was ${alert.comparator} ${alert.threshold} from ${since}` +
    `${latest === undefined ? "" : `, latest ${latest}`}. The alert "${alert.rule}" fired ${times}.`
  );
}
