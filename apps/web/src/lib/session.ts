// The access token lives in memory only. The refresh token is an HttpOnly cookie that page code cannot read.
let accessToken: string | null = null;

export const currentToken = () => accessToken;

export function authHeaders(): Record<string, string> {
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
}

let refreshing: Promise<boolean> | null = null;

/**
 * Trade the refresh cookie for a new access token; false when there is no live sign-in.
 * Callers at the same moment share one request: the server rotates the cookie on use and
 * treats a second use of the old one as theft, which would sign the user out.
 */
export function refreshSession(): Promise<boolean> {
  refreshing ??= (async () => {
    const response = await fetch("/api/auth/refresh", {
      method: "POST",
      headers: { "X-InfraWatch-Request": "1" },
    });
    accessToken = response.ok
      ? ((await response.json()) as { access_token: string }).access_token
      : null;
    return response.ok;
  })().finally(() => {
    refreshing = null;
  });
  return refreshing;
}

export async function signIn(email: string, password: string): Promise<boolean> {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (response.ok) {
    accessToken = ((await response.json()) as { access_token: string }).access_token;
  }
  return response.ok;
}
