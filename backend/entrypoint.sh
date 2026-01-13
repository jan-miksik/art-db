#!/bin/sh
set -e

# Materialize the Arweave wallet from an env var (base64) at startup.
if [ -n "${ARWEAVE_WALLET_B64:-}" ]; then
  SCRIPT_DIR="$(cd -- "$(dirname "$0")" && pwd)"
  DEFAULT_WALLET_PATH="$SCRIPT_DIR/media/arweave_wallet.json"
  WALLET_PATH="${ARWEAVE_WALLET_PATH:-$DEFAULT_WALLET_PATH}"
  WALLET_DIR="$(dirname "$WALLET_PATH")"

  mkdir -p "$WALLET_DIR"

  if printf '%s' "$ARWEAVE_WALLET_B64" | base64 -d > "$WALLET_PATH"; then
    chmod 600 "$WALLET_PATH"
    echo "Arweave wallet materialized at $WALLET_PATH"
  else
    echo "Failed to decode ARWEAVE_WALLET_B64; aborting startup" >&2
    exit 1
  fi
fi

python3 manage.py migrate
exec "$@"