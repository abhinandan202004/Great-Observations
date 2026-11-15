"""On-disk queue of unsent samples (ADR 0015).

Every write commits immediately, so a crash or restart loses nothing already buffered.
When full, the oldest samples are dropped and the drop is reported to the caller.
"""

import sqlite3
from pathlib import Path
from typing import NamedTuple

MAX_SAMPLES = 10_000


class Sample(NamedTuple):
    time: str
    metric: str
    value: float


class Buffer:
    def __init__(self, path: Path, max_samples: int = MAX_SAMPLES) -> None:
        self.max_samples = max_samples
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS samples (id INTEGER PRIMARY KEY,"
            " time TEXT NOT NULL, metric TEXT NOT NULL, value REAL NOT NULL)"
        )

    def add(self, samples: list[Sample]) -> int:
        """Store samples; return how many old samples were dropped to make room."""
        with self.db:
            self.db.executemany(
                "INSERT INTO samples (time, metric, value) VALUES (?, ?, ?)", samples
            )
            excess = len(self) - self.max_samples
            if excess > 0:
                self.db.execute(
                    "DELETE FROM samples WHERE id IN (SELECT id FROM samples ORDER BY id LIMIT ?)",
                    (excess,),
                )
        return max(excess, 0)

    def oldest(self, limit: int) -> tuple[int, list[Sample]]:
        """Return the id of the last sample in the batch, and the batch itself."""
        rows = self.db.execute(
            "SELECT id, time, metric, value FROM samples ORDER BY id LIMIT ?", (limit,)
        ).fetchall()
        return (rows[-1][0] if rows else 0), [Sample(*row[1:]) for row in rows]

    def remove_through(self, last_id: int) -> None:
        with self.db:
            self.db.execute("DELETE FROM samples WHERE id <= ?", (last_id,))

    def __len__(self) -> int:
        count: int = self.db.execute("SELECT count(*) FROM samples").fetchone()[0]
        return count
