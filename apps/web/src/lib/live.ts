"use client";

import { useEffect, useState } from "react";
import { currentToken, refreshSession } from "./session";

export const ALL = "*";
const UNAUTHENTICATED = 4401;
const RESYNC = 4409; // the server dropped us for falling behind: refetch everything
const QUIET_MS = 45_000; // heartbeats come every 20 s, so silence this long means a dead link
const BURST_MS = 50; // events this close together cause one refetch, not several

/** Wait before reconnect number ``attempt``: doubling from 1 s up to 30 s, with jitter. */
export function backoff(attempt: number, random = Math.random): number {
  const ceiling = Math.min(30_000, 1000 * 2 ** attempt);
  return ceiling / 2 + (random() * ceiling) / 2;
}

/**
 * Watch an incident (or ALL incidents) over the WebSocket gateway.
 * ``version`` goes up whenever the page should refetch; the socket itself carries no incident
 * data, so every refetch still goes through the REST API and its permission checks.
 */
export function useLive(target: string): { live: boolean; version: number } {
  const [live, setLive] = useState(false);
  const [version, setVersion] = useState(0);

  useEffect(() => {
    let cursor: number | null = null;
    let attempt = 0;
    let stopped = false;
    let socket: WebSocket | null = null;
    let retry: ReturnType<typeof setTimeout> | undefined;
    let quiet: ReturnType<typeof setTimeout> | undefined;
    let burst: ReturnType<typeof setTimeout> | undefined;
    let staleToken = false;

    const changed = () => {
      clearTimeout(burst);
      burst = setTimeout(() => setVersion((v) => v + 1), BURST_MS);
    };

    async function connect() {
      if ((staleToken || !currentToken()) && !(await refreshSession())) return; // signed out
      staleToken = false;
      if (stopped) return;
      const scheme = location.protocol === "https:" ? "wss" : "ws";
      const ws = new WebSocket(`${scheme}://${location.host}/api/ws`);
      socket = ws;
      const watch = () => {
        clearTimeout(quiet);
        quiet = setTimeout(() => ws.close(), QUIET_MS);
      };
      ws.onopen = () => {
        // The token goes in the first message, never in the URL.
        ws.send(JSON.stringify({ type: "auth", token: currentToken() }));
        ws.send(JSON.stringify({ type: "subscribe", target, after: cursor }));
        watch();
      };
      ws.onmessage = (message) => {
        watch();
        const data = JSON.parse(String(message.data));
        if (data.type === "ping") ws.send(JSON.stringify({ type: "pong" }));
        else if (data.type === "subscribed") {
          cursor = data.cursor;
          attempt = 0;
          setLive(true);
        } else if (data.type === "event") {
          cursor = target === ALL ? data.id : data.seq;
          changed();
        } else if (data.type === "refetch") changed();
      };
      ws.onclose = (event) => {
        clearTimeout(quiet);
        setLive(false);
        if (stopped) return;
        if (event.code === UNAUTHENTICATED) staleToken = true;
        if (event.code === RESYNC) {
          cursor = null;
          changed();
        }
        retry = setTimeout(connect, backoff(attempt++));
      };
    }

    connect();
    return () => {
      stopped = true;
      clearTimeout(retry);
      clearTimeout(quiet);
      clearTimeout(burst);
      socket?.close();
    };
  }, [target]);

  return { live, version };
}
