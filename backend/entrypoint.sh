#!/bin/sh
set -e

# Materialize the Arweave wallet from an env var (base64) at startup.
if [ -n "${ARWEAVE_WALLET_B64:-}" ]; then
  WALLET_PATH="/tmp/arweave_wallet.json"
  WALLET_DIR="$(dirname "$WALLET_PATH")"

  mkdir -p "$WALLET_DIR"

  if printf '%s' "$ARWEAVE_WALLET_B64" | base64 -d > "$WALLET_PATH"; then
    chmod 600 "$WALLET_PATH"
    echo "Arweave wallet materialized at $WALLET_PATH"
  else
    echo "Failed to decode ARWEAVE_WALLET_B64; aborting startup" >&2
    exit 1
  fi
else
  echo "ARWEAVE_WALLET_B64 is required; aborting startup" >&2
  exit 1
fi

python3 manage.py migrate
exec "$@"