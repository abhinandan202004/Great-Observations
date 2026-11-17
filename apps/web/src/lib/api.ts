/** GET from the InfraWatch API through the `/api` rewrite in next.config.ts. */
export async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`/api${path}`);
  if (!response.ok) {
    throw new Error(`The API answered ${response.status} for ${path}`);
  }
  return response.json();
}

export function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString();
}
