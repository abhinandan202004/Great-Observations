"use client";

import Link from "next/link";
import { type FormEvent, useEffect, useRef, useState } from "react";
import { getJson } from "@/lib/api";
import { CATEGORIES, type Category, type SearchHit, searchTerms, termRanges } from "@/lib/runbooks";

const HIGHLIGHT = "runbook-search";

export default function RunbooksPage() {
  const [hits, setHits] = useState<SearchHit[] | null>(null);
  const [asked, setAsked] = useState({ q: "", category: "" });
  const [error, setError] = useState("");
  const results = useRef<HTMLOListElement>(null);
  const query = asked.q;

  useEffect(() => {
    const params = new URLSearchParams();
    if (asked.q) params.set("q", asked.q);
    if (asked.category) params.set("category", asked.category);
    getJson<SearchHit[]>(`/runbooks/search?${params}`)
      .then((found) => {
        setHits(found);
        setError("");
      })
      .catch((reason) => setError(String(reason)));
  }, [asked]);

  function search(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const fields = new FormData(event.currentTarget);
    setAsked({
      q: String(fields.get("q") ?? "").trim(),
      category: String(fields.get("category") ?? ""),
    });
  }

  // Visual only, without touching the DOM: browsers without the API show plain, legible text.
  useEffect(() => {
    if (!("highlights" in CSS) || !results.current) return;
    CSS.highlights.delete(HIGHLIGHT);
    const ranges = termRanges(results.current, searchTerms(query));
    if (ranges.length) CSS.highlights.set(HIGHLIGHT, new Highlight(...ranges));
    return () => {
      CSS.highlights.delete(HIGHLIGHT);
    };
  }, [hits, query]);

  return (
    <main className="shell wide">
      <h1>Runbooks</h1>
      <search>
        <form className="filters" onSubmit={search} aria-label="Search approved runbooks">
          <div className="field">
            <label htmlFor="runbook-q">Words</label>
            <input
              id="runbook-q"
              name="q"
              type="search"
              maxLength={200}
              autoComplete="off"
              spellCheck={false}
              enterKeyHint="search"
            />
          </div>
          <div className="field">
            <label htmlFor="runbook-category">Root cause</label>
            <select id="runbook-category" name="category" defaultValue="">
              <option value="">Any</option>
              {Object.entries(CATEGORIES).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>
          <button type="submit">Search</button>
        </form>
      </search>
      {error && <p role="alert">{error}</p>}
      <p role="status">
        {hits && `${hits.length} approved runbook${hits.length === 1 ? "" : "s"}${query ? ` matching "${query}"` : ""}.`}
      </p>
      <ol ref={results} className="attachments">
        {hits?.map((hit) => (
          <li key={hit.incident_id}>
            <article aria-labelledby={`hit-${hit.incident_id}`}>
              <h2 id={`hit-${hit.incident_id}`}>
                <Link href={`/incidents/${hit.incident_id}`}>
                  #{hit.number} {hit.title}
                </Link>
              </h2>
              <p className="status">
                {CATEGORIES[hit.root_cause_category as Category]} · {hit.service} · version{" "}
                {hit.version}, approved{" "}
                <time dateTime={hit.approved_at}>{new Date(hit.approved_at).toLocaleDateString()}</time>
              </p>
              <p>{hit.excerpt}</p>
            </article>
          </li>
        ))}
      </ol>
    </main>
  );
}
