# Dockerfile for Quasar PWA with runtime tenant configuration

# Build stage: Install dependencies and prepare source
FROM node:24-alpine AS builder
WORKDIR /app

# Copy Yarn 4 configuration files and package.json
COPY .yarnrc.yml ./
COPY package.json yarn.lock ./

# Enable corepack for Yarn 4
RUN corepack enable

# Install dependencies
RUN yarn install --inline-builds

# Copy application source (config will be injected at runtime)
COPY . .

# Production stage: Lightweight runtime image
FROM node:24-alpine AS production
WORKDIR /app

# Install Quasar CLI globally using npm (Yarn 4 doesn't support global installs)
RUN npm install -g @quasar/cli

# Copy everything from builder
COPY --from=builder /app ./

# Enable corepack in production
RUN corepack enable

# Make startup script executable
RUN chmod +x ./scripts/startup.sh

# Expose port (default for quasar serve is 4000)
EXPOSE 4000

# Health check (longer timeout for initial build)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:4000/ || exit 1

# Run startup script that copies config, builds, and serves
CMD ["./scripts/startup.sh"]
