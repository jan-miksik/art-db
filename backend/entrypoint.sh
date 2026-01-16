#!/bin/sh
set -e

# Materialize the Arweave wallet from an env var (base64) at startup.
# Uses a secure random directory to prevent symlink attacks and path prediction.
if [ -n "${ARWEAVE_WALLET_B64:-}" ]; then
  # Create a secure, isolated temp directory with random suffix
  WALLET_DIR="$(mktemp -d -t arweave_wallet.XXXXXXXXXX)"
  
  # Restrict directory permissions to owner only (rwx------)
  chmod 700 "$WALLET_DIR"
  
  WALLET_PATH="${WALLET_DIR}/wallet.json"

  if printf '%s' "$ARWEAVE_WALLET_B64" | base64 -d > "$WALLET_PATH"; then
    # Restrict file permissions to owner read/write only (rw-------)
    chmod 600 "$WALLET_PATH"
    
    # Export for Django settings.py to read
    export ARWEAVE_WALLET_PATH="$WALLET_PATH"
    
    echo "Arweave wallet materialized at $WALLET_PATH"
  else
    echo "Failed to decode ARWEAVE_WALLET_B64; aborting startup" >&2
    rm -rf "$WALLET_DIR"
    exit 1
  fi
else
  echo "ARWEAVE_WALLET_B64 is required; aborting startup" >&2
  exit 1
fi

python3 manage.py migrate

# Create staticfiles directory and collect static files
mkdir -p staticfiles
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear
echo "Static files collected successfully"

exec "$@"