FROM node:22-alpine AS builder

WORKDIR /app

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
# VITE_MAPBOX_TOKEN is injected at build time via --build-arg / ARG
ARG VITE_MAPBOX_TOKEN
ENV VITE_MAPBOX_TOKEN=$VITE_MAPBOX_TOKEN

RUN pnpm build

# ---- Nginx serve ----
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
