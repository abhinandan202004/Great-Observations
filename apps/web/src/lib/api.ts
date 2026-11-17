import { authHeaders, refreshSession } from "./session";

/** Call the InfraWatch API through the `/api` rewrite in next.config.ts. */
export async function call<T>(method: string, path: string, body?: unknown): Promise<T> {
  const send = () =>
    fetch(`/api${path}`, {
      method,
      headers: {
        ...authHeaders(),
        ...(body === undefined ? {} : { "Content-Type": "application/json" }),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  let response = await send();
  // An expired access token is refreshed once; if that fails the user must sign in again.
  if (response.status === 401 && (await refreshSession())) {
    response = await send();
  }
  if (response.status === 401) {
    // A full load, not a client route change: it drops whatever the signed-out page still holds.
    // eslint-disable-next-line @next/next/no-location-assign-relative-destination
    window.location.assign("/login");
    throw new Error("Sign in again");
  }
  if (!response.ok) {
    throw new Error(`The API answered ${response.status} for ${path}`);
  }
  return response.json();
}

export const getJson = <T>(path: string) => call<T>("GET", path);
export const postJson = <T>(path: string, body: unknown) => call<T>("POST", path, body);

export function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString();
}
