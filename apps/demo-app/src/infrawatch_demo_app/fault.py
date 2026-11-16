"""Fault-injection command, run inside the demo-app container:

    docker compose exec demo-app python -m infrawatch_demo_app.fault error-burst
    docker compose exec demo-app python -m infrawatch_demo_app.fault cpu-spike --minutes 2
    docker compose exec demo-app python -m infrawatch_demo_app.fault stop

A fault stops by itself after --minutes (default 5). Only one runs at a time.
"""

import argparse
import os
import sys
import urllib.error
import urllib.request

from infrawatch_demo_app.faults import FAULTS


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m infrawatch_demo_app.fault")
    parser.add_argument("fault", choices=[*FAULTS, "stop"])
    parser.add_argument("--minutes", type=float, default=5, help="up to 60; default 5")
    args = parser.parse_args(argv)

    base = f"http://127.0.0.1:{os.environ.get('DEMO_APP_PORT', '8000')}/faults"
    if args.fault == "stop":
        request = urllib.request.Request(base, method="DELETE")
    else:
        url = f"{base}/{args.fault}?minutes={args.minutes}"
        request = urllib.request.Request(url, method="POST")  # noqa: S310  # fixed local URL
    try:
        with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310
            print(response.read().decode())
    except urllib.error.HTTPError as error:
        sys.exit(error.read().decode())


if __name__ == "__main__":
    main()
