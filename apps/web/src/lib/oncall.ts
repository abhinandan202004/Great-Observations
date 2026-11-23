export type Person = { id: string; display_name: string; email: string };

export type TeamOnCall = {
  team_id: string;
  team: string;
  group_email: string;
  rotation: {
    members: Person[];
    handover_local: string; // wall-clock time in time_zone, no offset
    time_zone: string;
    shift_days: number;
  } | null;
  on_call: Person | null;
  shift_ends_at: string | null;
};

export type UndeliveredEmail = {
  id: number;
  kind: string;
  subject: string;
  to_addresses: string[];
  created_at: string;
  attempts: number;
  next_attempt_at: string;
  last_error: string | null;
};

/** A copy of ``list`` with the item at ``from`` moved to ``to``. */
export function move<T>(list: readonly T[], from: number, to: number): T[] {
  const next = [...list];
  const [item] = next.splice(from, 1);
  next.splice(to, 0, item);
  return next;
}
