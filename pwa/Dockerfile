# Multi-stage Dockerfile for Quasar PWA production deployment

# Stage 1: Dependencies
FROM node:24-alpine AS deps
WORKDIR /app

# Copy Yarn 4 configuration files and package.json first
COPY .yarnrc.yml ./
COPY package.json yarn.lock ./

# Enable corepack for Yarn 4 after copying config files
RUN corepack enable

# Install dependencies using Yarn 4
RUN yarn install --immutable

# Stage 2: Builder
FROM node:24-alpine AS builder
WORKDIR /app

# Copy Yarn 4 configuration from deps stage
COPY --from=deps /app/.yarnrc.yml ./
COPY --from=deps /app/node_modules ./node_modules

# Enable corepack after copying config
RUN corepack enable

# Copy application files
COPY . .

# Create required config files from examples if they don't exist
RUN if [ ! -f settings.js ]; then cp settings_example.js settings.js; fi && \
    if [ ! -f src-pwa/manifest.json ]; then cp src-pwa/manifest_example.json src-pwa/manifest.json; fi && \
    if [ ! -f src/css/app.scss ]; then cp src/css/app_example.scss src/css/app.scss; fi

# Validate configuration before building
RUN yarn validate:config

# Build the PWA (validation is also included in build script)
RUN yarn build:pwa

# Stage 3: Production
FROM node:24-alpine AS production
WORKDIR /app

# Copy package.json and yarn config for corepack
COPY package.json yarn.lock ./
COPY .yarnrc.yml ./

# Enable corepack after copying config files
RUN corepack enable

# Install Quasar CLI globally for the serve command
RUN yarn global add @quasar/cli

# Copy built PWA from builder stage
COPY --from=builder /app/dist ./dist

# Expose port (default for quasar serve is 4000)
EXPOSE 4000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:4000/ || exit 1

# Serve the PWA using quasar serve
# --port: Server port
# --hostname: Server address (0.0.0.0 to accept connections from outside)
# --gzip: Enable gzip compression
# --history: Use history API fallback for SPA
# --cors: Enable CORS
CMD ["quasar", "serve", "dist/pwa/", "--port", "4000", "--hostname", "0.0.0.0", "--gzip", "--history", "--cors"]