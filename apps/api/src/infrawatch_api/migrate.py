"""``python -m infrawatch_api.migrate``: apply every migration to ``DATABASE_URL``.

Run as the owner role; the API itself connects as the application role.
"""

from alembic import command
from alembic.config import Config


def main() -> None:
    config = Config()
    config.set_main_option("script_location", "infrawatch_api:migrations")
    command.upgrade(config, "head")


if __name__ == "__main__":
    main()
