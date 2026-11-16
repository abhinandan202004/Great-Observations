"""Entry point: ``python -m infrawatch_api``."""

import logging
import os

import uvicorn


class _NoHealthFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "/health" not in record.getMessage()


def main() -> None:
    """Run the API with Uvicorn, configured from the environment."""
    logging.getLogger("uvicorn.access").addFilter(_NoHealthFilter())
    uvicorn.run(
        "infrawatch_api.main:app",
        host=os.environ.get("API_HOST", "0.0.0.0"),  # noqa: S104  # container listens on all interfaces
        port=int(os.environ.get("API_PORT", "8000")),
    )


if __name__ == "__main__":
    main()
