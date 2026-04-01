#!/bin/sh
#
# PWA Build script for deployment without Docker

set -e

# Configuration
TENANT_CONFIG_DIR="./tenant-config"
GENERATED_DIR="${TENANT_CONFIG_DIR}/overlay"
APP_DIR="./"

# Check if overlay config exists
if [ ! -d "$GENERATED_DIR" ]; then
  echo "[build-dist] ================================================================"
  echo "[build-dist] ERROR: Configuration not overlay!"
  echo "[build-dist] ================================================================"
  echo ""
  echo "[build-dist] The tenant-config/overlay/ directory is missing at:"
  echo "[build-dist]   $GENERATED_DIR"
  echo ""
  echo "[build-dist] This means the config has not been overlay before deployment."
  echo ""
  echo "[build-dist] To fix this:"
  echo "[build-dist]   1. Go to pwa-tenant-config-generator/"
  echo "[build-dist]   2. Run: yarn generate --config-dir tenant-configs/your-tenant"
  echo "[build-dist]   3. Ensure the overlay/ directory exists in your tenant config"
  echo "[build-dist]   4. Mount the complete tenant config directory to $APP_DIR/tenant-config"
  echo ""
  echo "[build-dist] Example Docker mount:"
  echo "[build-dist]   -v /path/to/tenant-configs/your-tenant:$APP_DIR/tenant-config:ro"
  echo ""
  echo "[build-dist] ================================================================"
  exit 1
fi

echo "[build-dist] Configuration"
echo "[build-dist]    Tenant config: $TENANT_CONFIG_DIR"
echo "[build-dist]    Generated dir: $GENERATED_DIR"
echo ""

# Copy overlay config over source
echo "[build-dist] Copying overlay config to project..."
echo ""

# Copy src/assets/
if [ -d "$GENERATED_DIR/src/assets" ]; then
  echo "[build-dist]    Copying src/assets/"
  mkdir -p $APP_DIR/src/assets/
  cp -r "$GENERATED_DIR/src/assets"/* $APP_DIR/src/assets/
fi

# Copy src/css/
if [ -d "$GENERATED_DIR/src/css" ]; then
  echo "[build-dist]    Copying src/css/"
  mkdir -p $APP_DIR/src/css/
  cp -r "$GENERATED_DIR/src/css"/* $APP_DIR/src/css/
fi

# Copy src-pwa/
if [ -d "$GENERATED_DIR/src-pwa" ]; then
  echo "[build-dist]    Copying src-pwa/"
  mkdir -p $APP_DIR/src-pwa/
  cp -r "$GENERATED_DIR/src-pwa"/* $APP_DIR/src-pwa/
fi

# Copy public/
if [ -d "$GENERATED_DIR/public" ]; then
  echo "[build-dist]    Copying public/"
  mkdir -p $APP_DIR/public/
  cp -r "$GENERATED_DIR/public"/* $APP_DIR/public/
fi

echo ""
echo "[build-dist] Configuration copied successfully"
echo ""

# Build the PWA
echo "[build-dist] Building PWA..."
echo ""
yarn build

if [ $? -ne 0 ]; then
  echo ""
  echo "[build-dist] Build failed!"
  exit 1
fi

echo ""
echo "[build-dist] Build complete"
echo "[build-dist] PWA is ready to be served from dist/pwa/"
echo ""

