"""Entry point: ``python -m infrawatch_demo_app``."""

import os

import uvicorn


def main() -> None:
    uvicorn.run(
        "infrawatch_demo_app.main:app",
        host=os.environ.get("DEMO_APP_HOST", "0.0.0.0"),  # noqa: S104  # container listens on all interfaces
        port=int(os.environ.get("DEMO_APP_PORT", "8000")),
    )


if __name__ == "__main__":
    main()
