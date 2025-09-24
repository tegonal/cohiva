# Docker Deployment for Cohiva PWA

This document explains how to build and deploy the Cohiva PWA using Docker with the Quasar serve command.

## Files Overview

- **Dockerfile**: Multi-stage build for production deployment with Node 24
- **docker-compose.yml**: Docker Compose configuration for easy deployment
- **.dockerignore**: Excludes unnecessary files from Docker build context

## How It Works

The Docker setup uses Quasar's built-in `quasar serve` command to serve the production build. This approach:

- Uses the official Quasar serving method
- Includes built-in gzip compression
- Supports SPA history mode
- Requires building the app first (done in the Dockerfile)

## Building the Docker Image

### Build for production:

```bash
docker build -t cohiva-pwa:latest .
```

### Build with specific tag:

```bash
docker build -t cohiva-pwa:v1.0.0 .
```

## Running the Container

### Using Docker directly:

```bash
# Run on default port 4000
docker run -d -p 4000:4000 --name cohiva-pwa cohiva-pwa:latest

# Run on custom port (e.g., 8080)
docker run -d -p 8080:4000 --name cohiva-pwa cohiva-pwa:latest
```

### Using Docker Compose:

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## Production Deployment

### Quasar Serve Features

The `quasar serve` command provides:

- **Port 4000**: Default serving port
- **Gzip compression**: Enabled by default for better performance
- **History mode**: Supports SPA routing with HTML5 history API
- **CORS support**: Enabled for cross-origin requests
- **Static file serving**: Optimized for production builds
