import { afterEach, expect, it, vi } from "vitest";
import { getJson, upload } from "./api";

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

it("shows the API's reason for a refusal", async () => {
  const refusal = JSON.stringify({ detail: "Only the caller may do this" });
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(refusal, { status: 403 })));

  await expect(getJson("/incidents")).rejects.toThrow("Only the caller may do this");
});

/** Answers each upload with the next status and body, reporting the body's size as progress. */
function fakeXhr(...replies: [number, string][]) {
  const sent: unknown[] = [];
  class FakeXhr {
    upload: { onprogress?: (event: ProgressEvent) => void } = {};
    onload?: () => void;
    status = 0;
    responseText = "";
    open() {}
    setRequestHeader() {}
    send(body: Blob) {
      sent.push(body);
      const [status, text] = replies.shift()!;
      this.upload.onprogress?.({ lengthComputable: true, loaded: body.size, total: body.size } as ProgressEvent);
      Object.assign(this, { status, responseText: text });
      this.onload?.();
    }
  }
  vi.stubGlobal("XMLHttpRequest", FakeXhr);
  return sent;
}

it("uploads the file as the body and reports progress", async () => {
  const sent = fakeXhr([201, JSON.stringify({ id: "a1" })]);
  const progress: number[] = [];
  const file = new Blob(["png bytes"]);

  await expect(upload("/x", file, (done, total) => progress.push(done / total))).resolves.toEqual({ id: "a1" });
  expect(sent).toEqual([file]);
  expect(progress).toEqual([1]);
});

it("shows why the server refused an upload", async () => {
  fakeXhr([415, JSON.stringify({ detail: "Only PNG, JPEG, GIF, WebP, PDF and .txt or .log text files are allowed" })]);

  await expect(upload("/x", new Blob(["<html>"]), () => {})).rejects.toThrow(/Only PNG/);
});
