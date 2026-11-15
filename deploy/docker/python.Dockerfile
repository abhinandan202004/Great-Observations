# Shared image definition for the InfraWatch Python services.
#
# Build from the repository root, selecting the workspace package and the
# module to run, for example:
#
#   docker build -f deploy/docker/python.Dockerfile \
#     --build-arg PACKAGE=infrawatch-api --build-arg MODULE=infrawatch_api \
#     -t infrawatch-api .
#
# See docs/adr/0016-continuous-integration-and-container-builds.md.

ARG PYTHON_IMAGE=python:3.12.13-slim-bookworm

# ------------------------------------------------------------------ build
FROM ${PYTHON_IMAGE} AS build

COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /src

ARG PACKAGE
RUN test -n "${PACKAGE}" || (echo "PACKAGE build argument is required" >&2 && exit 1)

COPY pyproject.toml uv.lock .python-version ./
COPY packages ./packages
COPY apps ./apps

RUN uv sync --frozen --no-dev --no-editable --package "${PACKAGE}"

# ---------------------------------------------------------------- runtime
FROM ${PYTHON_IMAGE} AS runtime

ARG MODULE
RUN test -n "${MODULE}" || (echo "MODULE build argument is required" >&2 && exit 1)

# /var/lib/infrawatch holds service state; a new named volume mounted there inherits its owner.
RUN groupadd --system app && useradd --system --gid app --no-create-home app \
    && install -d -o app -g app /var/lib/infrawatch

COPY --from=build /opt/venv /opt/venv

ENV PATH=/opt/venv/bin:${PATH} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_MODULE=${MODULE}

USER app

CMD ["sh", "-c", "exec python -m \"${APP_MODULE}\""]
