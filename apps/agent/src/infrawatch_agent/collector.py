"""Host metrics: CPU, memory, disk and network (G1.1)."""

import time
from datetime import UTC, datetime

import psutil

from infrawatch_agent.buffer import Sample


class Collector:
    def __init__(self) -> None:
        psutil.cpu_percent()  # the first reading has no baseline and is always 0.0
        self.last_net = psutil.net_io_counters()
        self.last_net_at = time.monotonic()

    def collect(self) -> list[Sample]:
        now = datetime.now(UTC).isoformat()
        net = psutil.net_io_counters()
        net_at = time.monotonic()
        elapsed = max(net_at - self.last_net_at, 0.001)  # coarse clocks can return equal readings
        values = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "net_sent_bytes_per_s": (net.bytes_sent - self.last_net.bytes_sent) / elapsed,
            "net_recv_bytes_per_s": (net.bytes_recv - self.last_net.bytes_recv) / elapsed,
        }
        self.last_net, self.last_net_at = net, net_at
        return [Sample(now, metric, float(value)) for metric, value in values.items()]
