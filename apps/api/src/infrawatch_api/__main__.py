"""Entry point: ``python -m infrawatch_api``."""

import os

import uvicorn


def main() -> None:
    """Run the API with Uvicorn, configured from the environment."""
    uvicorn.run(
        "infrawatch_api.main:app",
        host=os.environ.get("API_HOST", "0.0.0.0"),  # noqa: S104  # container listens on all interfaces
        port=int(os.environ.get("API_PORT", "8000")),
    )


if __name__ == "__main__":
    main()
