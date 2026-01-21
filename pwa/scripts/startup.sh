#!/bin/sh
#
# PWA Startup Script for Docker Container
#
# This script:
# 1. Copies overlay tenant configuration from mounted volume to /app
# 2. Builds the PWA with the tenant-specific configuration
# 3. Serves the built PWA on port 4000
#
# The tenant config must be mounted at /app/tenant-config containing:
#   - *.ts (settings.ts, theme.ts, schemas.ts)
#   - overlay/* (output from pwa-tenant-config-generator)
#

set -e

echo "[startup] PWA Startup Script"
echo "[startup] ===================="
echo ""

# Configuration
TENANT_CONFIG_DIR="/app/tenant-config"
GENERATED_DIR="${TENANT_CONFIG_DIR}/overlay"

# Check if overlay config exists
if [ ! -d "$GENERATED_DIR" ]; then
  echo "[startup] ================================================================"
  echo "[startup] ERROR: Configuration not overlay!"
  echo "[startup] ================================================================"
  echo ""
  echo "[startup] The tenant-config/overlay/ directory is missing at:"
  echo "[startup]   $GENERATED_DIR"
  echo ""
  echo "[startup] This means the config has not been overlay before deployment."
  echo ""
  echo "[startup] To fix this:"
  echo "[startup]   1. Go to pwa-tenant-config-generator/"
  echo "[startup]   2. Run: yarn generate --config-dir tenant-configs/your-tenant"
  echo "[startup]   3. Ensure the overlay/ directory exists in your tenant config"
  echo "[startup]   4. Mount the complete tenant config directory to /app/tenant-config"
  echo ""
  echo "[startup] Example Docker mount:"
  echo "[startup]   -v /path/to/tenant-configs/your-tenant:/app/tenant-config:ro"
  echo ""
  echo "[startup] ================================================================"
  exit 1
fi

echo "[startup] Configuration"
echo "[startup]    Tenant config: $TENANT_CONFIG_DIR"
echo "[startup]    Generated dir: $GENERATED_DIR"
echo ""

# Copy overlay config over source
echo "[startup] Copying overlay config to project..."
echo ""

# Copy src/assets/
if [ -d "$GENERATED_DIR/src/assets" ]; then
  echo "[startup]    Copying src/assets/"
  mkdir -p /app/src/assets/
  cp -r "$GENERATED_DIR/src/assets"/* /app/src/assets/
fi

# Copy src/css/
if [ -d "$GENERATED_DIR/src/css" ]; then
  echo "[startup]    Copying src/css/"
  mkdir -p /app/src/css/
  cp -r "$GENERATED_DIR/src/css"/* /app/src/css/
fi

# Copy src-pwa/
if [ -d "$GENERATED_DIR/src-pwa" ]; then
  echo "[startup]    Copying src-pwa/"
  mkdir -p /app/src-pwa/
  cp -r "$GENERATED_DIR/src-pwa"/* /app/src-pwa/
fi

# Copy public/
if [ -d "$GENERATED_DIR/public" ]; then
  echo "[startup]    Copying public/"
  mkdir -p /app/public/
  cp -r "$GENERATED_DIR/public"/* /app/public/
fi

echo ""
echo "[startup] Configuration copied successfully"
echo ""

# Build the PWA
echo "[startup] Building PWA..."
echo ""
quasar build -m pwa

if [ $? -ne 0 ]; then
  echo ""
  echo "[startup] Build failed!"
  exit 1
fi

echo ""
echo "[startup] Build complete"
echo ""

# Serve the PWA
echo "[startup] Starting server on port 4000..."
echo ""
exec quasar serve dist/pwa/ --port 4000 --hostname 0.0.0.0 --gzip --history --cors
