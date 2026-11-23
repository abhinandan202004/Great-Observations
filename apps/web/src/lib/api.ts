import { authHeaders, refreshSession } from "./session";

type Reply = { status: number; text: () => Promise<string> };

/** Send once, and once more after refreshing an expired access token; then check the answer. */
async function withSignIn<R extends Reply>(path: string, send: () => Promise<R>): Promise<R> {
  let reply = await send();
  if (reply.status === 401 && (await refreshSession())) {
    reply = await send();
  }
  if (reply.status === 401) {
    // A full load, not a client route change: it drops whatever the signed-out page still holds.
    // eslint-disable-next-line @next/next/no-location-assign-relative-destination
    window.location.assign("/login");
    throw new Error("Sign in again");
  }
  if (reply.status < 200 || reply.status >= 300) {
    // The API explains refusals in `detail`; validation errors carry a list there instead.
    const detail = await reply.text().then(
      (body) => JSON.parse(body)?.detail,
      () => undefined,
    );
    throw new Error(
      typeof detail === "string" ? detail : `The API answered ${reply.status} for ${path}`,
    );
  }
  return reply;
}

/** Call the InfraWatch API through the `/api` rewrite in next.config.ts. */
function request(method: string, path: string, body?: unknown): Promise<Response> {
  return withSignIn(path, () =>
    fetch(`/api${path}`, {
      method,
      headers: {
        ...authHeaders(),
        ...(body === undefined ? {} : { "Content-Type": "application/json" }),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    }),
  );
}

export async function call<T>(method: string, path: string, body?: unknown): Promise<T> {
  return (await request(method, path, body)).json();
}

export const getJson = <T>(path: string) => call<T>("GET", path);
export const postJson = <T>(path: string, body: unknown) => call<T>("POST", path, body);
export const putJson = <T>(path: string, body: unknown) => call<T>("PUT", path, body);
export const getBlob = async (path: string) => (await request("GET", path)).blob();

/**
 * POST a file as the raw request body, reporting progress as it goes.
 * XMLHttpRequest, not fetch: fetch cannot report how much of a request body has been sent.
 */
export async function upload<T>(
  path: string,
  file: Blob,
  onProgress: (sent: number, total: number) => void,
): Promise<T> {
  const send = () =>
    new Promise<Reply>((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", `/api${path}`);
      for (const [name, value] of Object.entries(authHeaders())) xhr.setRequestHeader(name, value);
      xhr.setRequestHeader("Content-Type", "application/octet-stream");
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) onProgress(event.loaded, event.total);
      };
      xhr.onload = () =>
        resolve({ status: xhr.status, text: () => Promise.resolve(xhr.responseText) });
      xhr.onerror = () => reject(new Error("The upload did not reach the server"));
      xhr.send(file);
    });
  return JSON.parse(await (await withSignIn(path, send)).text());
}

export function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString();
}
