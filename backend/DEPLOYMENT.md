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
railway variables set "ALLOWED_HOSTS=<you-domain>,localhost"
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
