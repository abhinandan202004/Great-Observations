"""Entry point: ``python -m infrawatch_demo_app``.

Skeleton only. The long-running process is implemented in a later milestone.
"""

import json
import sys

from infrawatch_demo_app import __version__


def main() -> None:
    """Emit a structured start-up record and exit."""
    record = {
        "service": "demo-app",
        "version": __version__,
        "message": "skeleton build; functionality not yet implemented",
    }
    sys.stdout.write(json.dumps(record) + "\n")


if __name__ == "__main__":
    main()
