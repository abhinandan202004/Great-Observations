// The access token lives in memory only. The refresh token is an HttpOnly cookie that page code cannot read.
let accessToken: string | null = null;

export const currentToken = () => accessToken;

export function authHeaders(): Record<string, string> {
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
}

/** Trade the refresh cookie for a new access token; false when there is no live sign-in. */
export async function refreshSession(): Promise<boolean> {
  const response = await fetch("/api/auth/refresh", {
    method: "POST",
    headers: { "X-InfraWatch-Request": "1" },
  });
  accessToken = response.ok
    ? ((await response.json()) as { access_token: string }).access_token
    : null;
  return response.ok;
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
