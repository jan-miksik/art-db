# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**a-db** is a full-stack art database application for browsing contemporary artists and artworks. Features include AI-powered image similarity search (Weaviate), decentralized image storage (Arweave), and an interactive bubble-based visualization interface.

## Development Commands

### Backend (Django)

```bash
# Start services and run server (from /backend)
docker compose up -d && source venv/bin/activate && export DJANGO_SETTINGS_MODULE=artist_registry.settings && python3 manage.py runserver

# Database migrations
python manage.py makemigrations
python3 manage.py migrate

# Create superuser for admin panel
python manage.py createsuperuser

# Stop services
docker compose down

# Virtual env setup (first time)
python3 -m venv venv
poetry install
```

### Frontend (Nuxt 4)

```bash
# From /frontend
yarn dev          # Development server (or yarn d)
yarn build        # Production build
yarn start        # Run production build
```

### Database Management

```bash
# Create database dump
docker exec -i backend-db-1 pg_dump -U postgres art_db -Ft > dump_$(date +%d-%m-%Y"_"%H_%M_%S).tar

# Recreate database from dump
docker exec -it backend-db-1 dropdb -U postgres art_db && \
docker exec -it backend-db-1 createdb -U postgres art_db && \
cat <dump_file>.tar | docker exec -i backend-db-1 pg_restore -U postgres -d art_db
```

## Architecture

### Tech Stack
- **Backend**: Django 5.2 + Django REST Framework, PostgreSQL, Weaviate (vector DB)
- **Frontend**: Nuxt 4, Vue 3, Pinia 3, Stylus
- **Storage**: Arweave (decentralized), IndexedDB (client-side caching)

### Key Directories

```
backend/
├── artists/              # Main Django app
│   ├── models.py         # Artist & Artwork models
│   ├── views.py          # API endpoints
│   ├── weaviate/         # AI vector search integration
│   └── admin.py          # Custom admin with Arweave upload
└── docker-compose.yml    # PostgreSQL + Weaviate services

frontend/
├── pages/index.vue       # Main application page
├── components/           # Vue components (Artist.vue, ArtistModal.vue, Filter.vue, etc.)
├── composables/          # Vue composables (useFocusTrap, useArtistArrangement, etc.)
├── J/                    # Pinia stores (useArtistsStore, useFilterStore, useSortStore)
├── models/               # TypeScript types (IImageFile, etc.)
└── services/idb.ts       # IndexedDB caching via Dexie
```

### Dual View System
The UI has two modes:
- **Bubble View**: Interactive draggable artist cards using Interact.js
- **Table View**: Traditional sortable table using TanStack Table

### AI Image Search (Weaviate)
- Weaviate runs in Docker with img2vec-neural (ResNet50)
- Search by image URL or file upload
- Endpoints: `/artists/search-artworks-by-image-url/`, `/artists/search-authors-by-image-url/`
- Similar artists pre-computed and stored in `similar_authors_postgres_ids` field

### Arweave Integration
- Images uploaded to Arweave via admin panel (auto-upload on save)
- Wallet stored in `/backend/media/`
- URLs stored in Artist/Artwork models

### Client-Side Caching
- IndexedDB via Dexie stores image blobs locally
- `BaseImage.vue` component handles caching and fallback images

### State Management (Pinia)
- `useArtistsStore`: Full artist dataset + filtered view
- `useFilterStore`: Text search, range filtering (birth year), gender, media type
- `useSortStore`: Sorting by name, birth year, auction turnover
- All filtering/sorting happens client-side on the full dataset

### API Endpoints
- `GET /artists/` - List all artists with nested artworks
- `POST /artists/upload-to-arweave/<id>/` - Upload artist image
- `GET /artists/search-artworks-by-image-url/` - AI similarity search
- `POST /artists/search-artworks-by-image-data/` - AI search with uploaded image

## Branch Strategy
- `main` - development
- `be-prod` - backend production
- `fe-prod` - frontend production
