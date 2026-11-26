import { afterEach, expect, it, vi } from "vitest";
import { currentToken, refreshSession } from "./session";

afterEach(() => vi.unstubAllGlobals());

it("shares one refresh between callers at the same moment", async () => {
  const fetch = vi.fn(async () => new Response(JSON.stringify({ access_token: "fresh" })));
  vi.stubGlobal("fetch", fetch);

  const answers = await Promise.all([refreshSession(), refreshSession(), refreshSession()]);

  expect(answers).toEqual([true, true, true]);
  expect(fetch).toHaveBeenCalledTimes(1);
  expect(currentToken()).toBe("fresh");
});

it("asks again once the earlier refresh has finished", async () => {
  const fetch = vi.fn(async () => new Response(JSON.stringify({ access_token: "again" })));
  vi.stubGlobal("fetch", fetch);

  await refreshSession();
  await refreshSession();

  expect(fetch).toHaveBeenCalledTimes(2);
});
