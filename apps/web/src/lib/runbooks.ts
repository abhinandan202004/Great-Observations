export const CATEGORIES = {
  code_or_deploy: "Code or deploy",
  configuration: "Configuration",
  capacity_or_infrastructure: "Capacity or infrastructure",
  dependency_or_third_party: "Dependency or third party",
  data: "Data",
  security: "Security",
  process_or_human: "Process or human",
} as const;
export type Category = keyof typeof CATEGORIES;

/** The six required fields; similar incidents is answered by links or by a statement. */
export type RunbookFields = {
  timeline: string;
  root_cause_category: Category;
  root_cause: string;
  contributing_factors: string;
  remediation: string;
  workaround: string;
  none_similar: string;
};

export type Version = RunbookFields & {
  version: number;
  author: string;
  created_at: string;
  similar_incidents: { id: string; number: number; title: string }[];
  review: { decision: "approved" | "returned"; reviewer: string; reviewed_at: string; comment: string } | null;
};

export type Runbook = {
  categories: Category[];
  suggested_timeline: string;
  may_close: boolean;
  pending_version: number | null;
  versions: Version[];
};

export type SearchHit = {
  incident_id: string;
  number: number;
  title: string;
  service: string;
  version: number;
  root_cause_category: Category;
  approved_at: string;
  excerpt: string;
};

/** The words worth highlighting in a search: no operators, quotes or one-letter words. */
export function searchTerms(query: string): string[] {
  const words = query
    .toLowerCase()
    .split(/\s+/)
    .map((word) => word.replace(/^-|["']/g, ""))
    .filter((word) => word.length > 1 && word !== "or");
  return [...new Set(words)];
}

/** Ranges over every case-insensitive occurrence of the terms in the text under ``root``. */
export function termRanges(root: Node, terms: string[]): Range[] {
  const ranges: Range[] = [];
  if (terms.length === 0) return ranges;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    const text = (node.textContent ?? "").toLowerCase();
    for (const term of terms) {
      for (let at = text.indexOf(term); at !== -1; at = text.indexOf(term, at + term.length)) {
        const range = new Range();
        range.setStart(node, at);
        range.setEnd(node, at + term.length);
        ranges.push(range);
      }
    }
  }
  return ranges;
}
