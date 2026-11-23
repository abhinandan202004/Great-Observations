import type { Point } from "@/app/telemetry/chart";

type Base = {
  id: string;
  title: string;
  created_by: string;
  created_at: string;
  file_name: string | null;
  content_type: string | null;
  size_bytes: number | null;
};

export type LogLine = {
  id?: string;
  time: string;
  service: string;
  level: string;
  message: string;
  correlation_id: string | null;
};

/** Each kind carries the evidence the API copied when it was attached. */
export type Attachment = Base &
  (
    | {
        kind: "metric_snapshot";
        data: { service: string; metric: string; since: string; until: string; points: Point[] };
      }
    | { kind: "log_excerpt"; data: { lines: LogLine[] } }
    | { kind: "link" | "note"; data: { text: string; url: string | null } }
    | { kind: "file"; data: Record<string, never> }
  );

export const MAX_FILE_BYTES = 10 * 1024 * 1024;
export const ACCEPTED_FILES = "image/png,image/jpeg,image/gif,image/webp,application/pdf,.txt,.log";

export function formatBytes(bytes: number): string {
  const [value, unit] =
    bytes >= 1024 * 1024 ? [bytes / 1024 / 1024, "megabyte"] : [bytes / 1024, "kilobyte"];
  return new Intl.NumberFormat(undefined, {
    style: "unit",
    unit,
    unitDisplay: "short",
    maximumFractionDigits: 1,
  }).format(value);
}

/** Save fetched bytes under their original name, then let the temporary URL go. */
export function saveFile(blob: Blob, name: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url));
}
