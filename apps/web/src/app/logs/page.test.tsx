import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import LogsPage from "./page";

afterEach(() => vi.unstubAllGlobals());

describe("LogsPage", () => {
  it("sends the chosen filters and shows the entries with correlation IDs", async () => {
    const entry = {
      time: "2026-11-17T10:00:00Z",
      service: "checkout",
      level: "error",
      message: "checkout failed",
      correlation_id: "abc123",
    };
    const fetchMock = vi.fn(async (url: string) =>
      Response.json(url === "/api/services" ? ["checkout"] : [entry]),
    );
    vi.stubGlobal("fetch", fetchMock);

    render(<LogsPage />);
    await screen.findByRole("option", { name: "checkout" });
    fireEvent.change(screen.getByLabelText("Service"), {
      target: { value: "checkout" },
    });
    fireEvent.change(screen.getByLabelText("Level"), {
      target: { value: "error" },
    });
    fireEvent.change(screen.getByLabelText("Text or correlation ID"), {
      target: { value: "failed" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Search" }));

    expect(await screen.findByText("abc123")).toBeDefined();
    const query = new URL(fetchMock.mock.calls[1][0], "http://web").searchParams;
    expect(query.get("service")).toBe("checkout");
    expect(query.get("level")).toBe("error");
    expect(query.get("q")).toBe("failed");
    expect(query.get("since")).toMatch(/Z$/);
    expect(query.has("until")).toBe(false);
  });
});
