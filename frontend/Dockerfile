# syntax=docker/dockerfile:1

FROM node:22-alpine AS base
WORKDIR /app

# --- deps: install once, reused by both the dev and builder stages ---
FROM base AS deps
COPY package.json package-lock.json ./
RUN npm ci

# --- dev: `next dev` against the bind-mounted source (see docker-compose.yml) ---
FROM base AS dev
ENV NODE_ENV=development
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]

# --- builder: production build, traced down to `.next/standalone`
# (requires `output: "standalone"` in next.config.ts) ---
FROM base AS builder
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# --- runner: only the standalone output + static assets, non-root user ---
FROM base AS runner
ENV NODE_ENV=production \
    PORT=3000 \
    HOSTNAME=0.0.0.0

RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
