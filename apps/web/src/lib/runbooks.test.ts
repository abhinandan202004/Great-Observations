import { describe, expect, it } from "vitest";
import { searchTerms, termRanges } from "./runbooks";

describe("searchTerms", () => {
  it("keeps the words, without search operators, quotes or duplicates", () => {
    expect(searchTerms('"payment retry" -cache Retry or db x')).toEqual(["payment", "retry", "cache", "db"]);
  });
});

describe("termRanges", () => {
  it("finds every occurrence across text nodes, ignoring case", () => {
    const root = document.createElement("div");
    root.innerHTML = "<p>Retry the <b>retry</b> queue</p><p>no match</p>";

    const found = termRanges(root, ["retry"]).map((range) => range.toString());

    expect(found).toEqual(["Retry", "retry"]);
  });

  it("finds nothing without terms", () => {
    expect(termRanges(document.body, [])).toEqual([]);
  });
});
