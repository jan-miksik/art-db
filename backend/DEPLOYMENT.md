# Railway Deployment Guide

Guide for deploying the Django backend to Railway.

## Prerequisites

1. Railway account: [railway.app](https://railway.app)
2. Railway CLI: `brew install railway` or `npm i -g @railway/cli`

## Setup

### 1. Login and Link

```bash
railway login
railway link
# Select your project and django-server service
```

### 2. Set Environment Variables

In Railway dashboard or by railway CLI

**Required variables:**

```bash
# Generate secret key
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Set variables
railway variables set "DJANGO_SECRET_KEY=<generated-key>"
railway variables set "DJANGO_ENV=production"
railway variables set "DEBUG=False"
railway variables set "ALLOWED_HOSTS=<your-domain>,localhost"
railway variables set "CORS_ALLOWED_ORIGINS=https://your-frontend.com,http://localhost:3000"
railway variables set "ARWEAVE_WALLET_B64=<base64-encoded-wallet>"
```

**Get your Railway domain:**
```bash
railway domain
```

**Encode Arweave wallet:**
```bash
# macOS
base64 arweave_wallet.json

# Linux
base64 -w 0 arweave_wallet.json
```

### 3. Deploy

```bash
railway up
```

### 4. Post-Deploy Steps

**Automated Commands (No Action Required):**

✅ **Database Migrations** - Run automatically via `entrypoint.sh` on every container startup. The script executes `python manage.py migrate` before starting the server, so migrations are applied automatically with each deployment.

✅ **Static File Collection** - Handled at Docker build time. The `Dockerfile` runs `collectstatic --noinput` during the image build process, so static files are collected automatically when the image is built.

**Manual Commands (Run Once When Needed):**

**Create Superuser (One-time setup):**
```bash
railway run python manage.py createsuperuser
```
Only needed when setting up a new deployment environment. Run this once to create your first admin user for accessing the Django admin panel.

**Note:** The automation is configured in:
- `entrypoint.sh` (line 33) - Runs migrations before server startup
- `Dockerfile` (line 26) - Collects static files at build time

No manual intervention is needed for migrations or static files after deployment. They run automatically!

## Common Commands

```bash
railway status           # Check connection
railway variables        # View all variables
railway logs --follow    # View logs
railway open            # Open dashboard
railway domain          # Get deployment URL
```

## Troubleshooting

**Build timeout:** Large files are being uploaded. Ensure `.railwayignore` and `.dockerignore` exclude `venv/` and `media/`.

For more details, see [Railway Docs](https://docs.railway.app).
