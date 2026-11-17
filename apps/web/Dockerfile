# Image definition for the InfraWatch web application.
# Build from the repository root:
#
#   docker build -f apps/web/Dockerfile -t infrawatch-web .

ARG NODE_IMAGE=node:22.19.0-alpine3.22

# ----------------------------------------------------------- dependencies
FROM ${NODE_IMAGE} AS deps
WORKDIR /app
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci --no-audit --no-fund

# ------------------------------------------------------------------ build
FROM ${NODE_IMAGE} AS build
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
# Where the /api rewrite sends requests: the API's name on the Compose network.
ARG API_URL=http://api:8000
ENV API_URL=${API_URL}
COPY --from=deps /app/node_modules ./node_modules
COPY apps/web/ ./
RUN npm run build

# ---------------------------------------------------------------- runtime
FROM ${NODE_IMAGE} AS runtime
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

RUN addgroup -S app && adduser -S app -G app

COPY --from=build --chown=app:app /app/.next/standalone ./
COPY --from=build --chown=app:app /app/.next/static ./.next/static
COPY --from=build --chown=app:app /app/public ./public

USER app
EXPOSE 3000

CMD ["node", "server.js"]
