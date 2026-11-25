/**
 * The live-update state: visible text that changes quietly, and a separate status region that
 * speaks only for a long outage and its end. Announcing every brief reconnect would be noise.
 */
export function LiveStatus({ live, notice }: { live: boolean; notice: string }) {
  return (
    <>
      <p className="status">{live ? "Live: updates appear as they happen" : "Connecting for live updates…"}</p>
      <p role="status" className="visually-hidden">
        {notice}
      </p>
    </>
  );
}
