/** Incident types from the API, and the lifecycle rules the page uses to offer moves. */

import type { FiredAlert } from "./drafts";

export const STATES = [
  "raised",
  "acknowledged",
  "investigating",
  "mitigating",
  "monitoring",
  "resolved",
  "closed",
] as const;
export type Status = (typeof STATES)[number];
export const SEVERITIES = ["P1", "P2", "P3", "P4"] as const;

export type SlaTimer = {
  due: string;
  stopped_at: string | null;
  remaining_seconds: number;
  breached: boolean;
};

export type Summary = {
  id: string;
  number: number;
  title: string;
  impact: string;
  severity: string;
  status: Status;
  service: string;
  raised_at: string;
  acknowledge: SlaTimer;
  resolve: SlaTimer;
};

export type TeamTask = {
  team_id: string;
  team: string;
  assignee_id: string | null;
  assignee: string | null;
  checklist: { id: string; text: string; done: boolean }[];
};

export type Detail = Summary & {
  description: string;
  caller: string;
  teams: TeamTask[];
  timeline: {
    id: number;
    time: string;
    actor: string;
    from_status: Status | null;
    to_status: Status;
    reason: string | null;
    reopens: number | null;
  }[];
  alerts: FiredAlert[];
};

export type Team = {
  id: string;
  name: string;
  members: { id: string; display_name: string; is_lead: boolean }[];
};

const ACTIVE_COUNT = 5; // raised to monitoring

/** The moves to offer from a status. The API checks them again; this only shapes the buttons. */
export function moves(current: Status): {
  forward: Status | null;
  back: Status[];
  callerOnly: boolean;
} {
  const index = STATES.indexOf(current);
  if (index < ACTIVE_COUNT) {
    return { forward: STATES[index + 1], back: [...STATES.slice(0, index)], callerOnly: false };
  }
  return { forward: null, back: [], callerOnly: current === "resolved" };
}

/** "12m left", "overdue by 1h 5m", "met with 3m to spare" — the clock keeps running until met. */
export function timerText(timer: SlaTimer, now: number): { text: string; breached: boolean } {
  const running = timer.stopped_at === null;
  const seconds = running
    ? Math.round((Date.parse(timer.due) - now) / 1000)
    : timer.remaining_seconds;
  const span = duration(Math.abs(seconds));
  if (!running) {
    return seconds >= 0
      ? { text: `met with ${span} to spare`, breached: false }
      : { text: `met ${span} late`, breached: true };
  }
  return seconds >= 0
    ? { text: `${span} left`, breached: false }
    : { text: `overdue by ${span}`, breached: true };
}

type DurationFormat = new (
  locale?: string,
  options?: { style: "narrow"; minutesDisplay: "always" },
) => { format(duration: { days: number; hours: number; minutes: number }): string };

/** A span in days, hours and minutes, localised by Intl.DurationFormat where the browser has it. */
function duration(seconds: number): string {
  const total = Math.floor(seconds / 60);
  const balanced = {
    days: Math.floor(total / 1440),
    hours: Math.floor((total % 1440) / 60),
    minutes: total % 60,
  };
  // Not yet in this TypeScript's lib, and missing from Node 22 and pre-2025 browsers.
  const Format = (Intl as unknown as { DurationFormat?: DurationFormat }).DurationFormat;
  if (Format) {
    return new Format(undefined, { style: "narrow", minutesDisplay: "always" }).format(balanced);
  }
  const { days, hours, minutes } = balanced;
  return [days && `${days}d`, hours && `${hours}h`, `${minutes}m`].filter(Boolean).join(" ");
}
