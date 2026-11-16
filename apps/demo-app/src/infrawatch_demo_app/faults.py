"""Fault injection state: one fault at a time, each stopping itself at its time limit."""

import os
import subprocess
import sys
import time
from collections.abc import Callable

FAULTS = ("cpu-spike", "error-burst", "bad-deploy", "dependency-latency")

# Niced so the spike shows as saturated CPU without starving the rest of the stack.
BURNER = "import os\nif hasattr(os, 'nice'): os.nice(10)\nwhile True: pass"


class FaultActiveError(Exception):
    pass


class Faults:
    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self.clock = clock
        self.name: str | None = None
        self.until = 0.0
        self.burners: list[subprocess.Popen[bytes]] = []

    def active(self) -> str | None:
        """The running fault, if any. Also where an expired fault is stopped."""
        if self.name and self.clock() >= self.until:
            self.stop()
        return self.name

    def start(self, name: str, minutes: float) -> None:
        running = self.active()
        if running:
            raise FaultActiveError(running)
        self.name, self.until = name, self.clock() + minutes * 60
        if name == "cpu-spike":
            self.burners = [
                subprocess.Popen([sys.executable, "-c", BURNER])  # noqa: S603  # fixed arguments
                for _ in range(os.cpu_count() or 1)
            ]

    def stop(self) -> None:
        for burner in self.burners:
            burner.kill()
            burner.wait()
        self.burners = []
        self.name = None
