# Environment Configuration Setup

This project uses environment-specific configuration files for different deployment environments.

## Quick Start

1. **For Local Development:**
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your local settings
   ```

2. **For Production:**
   ```bash
   cp .env.production.example .env.production
   # Edit .env.production with your production secrets
   ```

## Environment Files

- `.env.local` - Local development (gitignored, safe for local secrets) - **REQUIRED for local dev**
- `.env.production` - Production environment (gitignored, NEVER commit) - **REQUIRED for production**
- `.env.example` - General template showing all available variables
- `.env.local.example` - Template for local development
- `.env.production.example` - Template for production

## How It Works

The `settings.py` file automatically loads the appropriate environment file based on the `DJANGO_ENV` environment variable:

- `DJANGO_ENV=local` (default) → loads `.env.local` (required)
- `DJANGO_ENV=production` → loads `.env.production` (required)

**Note:** Environment-specific files are required. The application will fail to start if the expected file doesn't exist.

## Required Variables

### All Environments
- `DJANGO_SECRET_KEY` - Django secret key (REQUIRED)
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `PGDATABASE`, `PGUSER`, `POSTGRES_PASSWORD`, `PGHOST`, `PGPORT` - Database config
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of allowed CORS origins

### Required
- `ARWEAVE_WALLET_B64` - Base64-encoded contents of `arweave_wallet.json` (mandatory)

## Arweave wallet in production (Railway)

Set the wallet file as an env var and let the entrypoint write it to disk on boot:

1. Base64 the wallet locally (no newlines): `base64 -w 0 arweave_wallet.json` (macOS: `base64 arweave_wallet.json`)
2. Add the value to Railway as `ARWEAVE_WALLET_B64`
3. Wallet is written to a secure, randomly-named temp directory (e.g., `/tmp/arweave_wallet.XXXXXXXXXX/wallet.json`) with restricted permissions
4. On start, `entrypoint.sh` creates the secure directory (0700), decodes the wallet (0600), and exports `ARWEAVE_WALLET_PATH` for Django

## Security Notes

- ✅ `.env.local` and `.env.production` are gitignored
- ✅ Example files (`.env.*.example`) are safe to commit
- ❌ NEVER commit actual `.env` files with secrets
- ❌ NEVER use `DEBUG=True` in production
- ❌ NEVER use weak passwords or default secrets in production
- 🔒 Arweave wallet is stored in a randomly-named temp directory (prevents symlink attacks and path prediction)
- 🔒 Directory permissions: `0700` (owner rwx only), file permissions: `0600` (owner rw only)
- 🔒 `ARWEAVE_WALLET_B64` env var is mandatory; startup fails if missing or invalid

## Generating a Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
