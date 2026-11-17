import { afterEach, expect, it, vi } from "vitest";
import { getJson } from "./api";

afterEach(() => vi.unstubAllGlobals());

it("refreshes the sign-in once after a 401 and retries with the new token", async () => {
  const fetch = vi
    .fn()
    .mockResolvedValueOnce(new Response("", { status: 401 }))
    .mockResolvedValueOnce(new Response(JSON.stringify({ access_token: "new" }), { status: 200 }))
    .mockResolvedValueOnce(new Response(JSON.stringify(["checkout"]), { status: 200 }));
  vi.stubGlobal("fetch", fetch);

  await expect(getJson<string[]>("/services")).resolves.toEqual(["checkout"]);
  expect(fetch.mock.calls[2][1].headers).toEqual({ Authorization: "Bearer new" });
});
