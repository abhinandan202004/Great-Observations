import { act, cleanup, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { backoff, OUTAGE, RESTORED, useLive } from "./live";

const session = vi.hoisted(() => ({ token: "token" as string | null, refresh: async () => true }));
vi.mock("./session", () => ({
  currentToken: () => session.token,
  refreshSession: () => session.refresh(),
}));

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
  session.token = "token";
  session.refresh = async () => true;
  vi.stubGlobal("WebSocket", FakeSocket);
});
afterEach(() => {
  cleanup(); // unmount, so earlier hooks do not answer this test's events
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

async function opened(socket = FakeSocket.all.at(-1)!) {
  socket.onopen?.();
  return socket;
}

it("stops for good when the server refuses this role", async () => {
  renderHook(() => useLive("abc"));
  await act(async () => {});
  const socket = await opened();
  act(() => socket.onclose?.({ code: 4403 }));

  await act(async () => {
    vi.advanceTimersByTime(120_000);
  });
  expect(FakeSocket.all).toHaveLength(1);
});

it("retries when renewing the sign-in fails on the network", async () => {
  session.token = null;
  session.refresh = () => Promise.reject(new TypeError("Failed to fetch"));
  renderHook(() => useLive("abc"));
  await act(async () => {});
  expect(FakeSocket.all).toHaveLength(0);

  session.refresh = async () => {
    session.token = "token";
    return true;
  };
  await act(async () => {
    vi.advanceTimersByTime(1000);
  });
  expect(FakeSocket.all).toHaveLength(1);
});

it("reconnects at once when the browser comes back online", async () => {
  renderHook(() => useLive("abc"));
  await act(async () => {});
  const socket = await opened();
  act(() => socket.onclose?.({ code: 1006 }));

  await act(async () => {
    window.dispatchEvent(new Event("online"));
  });
  expect(FakeSocket.all).toHaveLength(2);
});

it("announces a long outage once, and its end", async () => {
  const { result } = renderHook(() => useLive("abc"));
  await act(async () => {});
  const first = await opened();
  act(() => first.receive({ type: "subscribed", target: "abc", cursor: 1 }));
  act(() => first.onclose?.({ code: 1006 }));
  expect(result.current.notice).toBe("");

  // Every retry fails, so the outage outlasts ten seconds.
  await act(async () => {
    for (let i = 0; i < 5; i++) {
      vi.advanceTimersByTime(3000);
      FakeSocket.all.at(-1)?.onclose?.({ code: 1006 });
    }
  });
  expect(result.current.notice).toBe(OUTAGE);

  const back = await opened();
  act(() => back.receive({ type: "subscribed", target: "abc", cursor: 1 }));
  expect(result.current.notice).toBe(RESTORED);
});
