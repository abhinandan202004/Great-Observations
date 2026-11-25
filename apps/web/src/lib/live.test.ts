import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { backoff, useLive } from "./live";

vi.mock("./session", () => ({ currentToken: () => "token", refreshSession: async () => true }));

class FakeSocket {
  static all: FakeSocket[] = [];
  sent: unknown[] = [];
  onopen?: () => void;
  onmessage?: (message: { data: string }) => void;
  onclose?: (event: { code: number }) => void;
  constructor(public url: string) {
    FakeSocket.all.push(this);
  }
  send(data: string) {
    this.sent.push(JSON.parse(data));
  }
  close() {}
  receive(data: object) {
    this.onmessage?.({ data: JSON.stringify(data) });
  }
}

beforeEach(() => {
  vi.useFakeTimers();
  FakeSocket.all = [];
  vi.stubGlobal("WebSocket", FakeSocket);
});
afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

it("signs in, subscribes from now, and refetches on each event", async () => {
  const { result } = renderHook(() => useLive("abc"));
  await act(async () => {});
  const socket = FakeSocket.all[0];
  socket.onopen?.();

  expect(socket.url).toMatch(/\/api\/ws$/);
  expect(socket.sent).toEqual([
    { type: "auth", token: "token" },
    { type: "subscribe", target: "abc", after: null },
  ]);

  act(() => socket.receive({ type: "subscribed", target: "abc", cursor: 4 }));
  expect(result.current.live).toBe(true);
  act(() => {
    socket.receive({ type: "event", incident: "abc", seq: 5, id: 90, kind: "status" });
    socket.receive({ type: "event", incident: "abc", seq: 6, id: 91, kind: "status" });
    vi.advanceTimersByTime(100);
  });
  expect(result.current.version).toBe(1); // a burst is one refetch
});

it("reconnects after a drop and resumes from the last event it saw", async () => {
  const { result } = renderHook(() => useLive("abc"));
  await act(async () => {});
  const first = FakeSocket.all[0];
  first.onopen?.();
  act(() => {
    first.receive({ type: "subscribed", target: "abc", cursor: 4 });
    first.receive({ type: "event", incident: "abc", seq: 5, id: 90, kind: "status" });
    first.onclose?.({ code: 1006 });
  });
  expect(result.current.live).toBe(false);

  await act(async () => {
    vi.advanceTimersByTime(1000);
  });
  const second = FakeSocket.all[1];
  second.onopen?.();
  expect(second.sent[1]).toEqual({ type: "subscribe", target: "abc", after: 5 });
});

it("answers heartbeats", async () => {
  renderHook(() => useLive("abc"));
  await act(async () => {});
  const socket = FakeSocket.all[0];
  socket.onopen?.();
  socket.receive({ type: "ping" });

  expect(socket.sent.at(-1)).toEqual({ type: "pong" });
});

it("backs off from about a second to at most thirty", () => {
  expect(backoff(0, () => 0)).toBe(500);
  expect(backoff(0, () => 1)).toBe(1000);
  expect(backoff(10, () => 1)).toBe(30_000);
});
