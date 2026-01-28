# Railway Deployment Guide

Guide for deploying the Nuxt 4 frontend to Railway.

## Prerequisites

1. Railway account: [railway.app](https://railway.app)
2. Railway CLI: `brew install railway` or `npm i -g @railway/cli`

## Setup

### 1. Login and Link

```bash
railway login
railway link
# Select your project and frontend service
```

### 2. Set Environment Variables

In Railway dashboard or by railway CLI

Set `DJANGO_SERVER_URL` to your backend API URL:

```bash
railway variables set "DJANGO_SERVER_URL=https://your-backend.up.railway.app"
```

Replace `your-backend.up.railway.app` with your actual backend Railway domain.

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

For more details, see [Railway Docs](https://docs.railway.app) and [Nuxt Deployment Docs](https://nuxt.com/docs/getting-started/deployment).
