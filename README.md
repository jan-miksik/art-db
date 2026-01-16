# Art-db

A full-stack art database application for browsing contemporary artists and artworks.

**Live Application**: [Deployed on Railway](https://a-db-production.up.railway.app/)

## Features

- **Decentralized Storage**: Images stored on Arweave blockchain for permanent, decentralized access
- **Interactive UI**: Dual view system with draggable bubble view and sortable table view
- **Client-Side Caching**: IndexedDB caching for offline image access
- **Advanced Filtering**: Filter by text search, birth year, gender, and media type
- **Real-time Sorting**: Sort by name, birth year, or auction turnover

## Tech Stack

### Frontend

- **Framework**: Nuxt 4 (Vue 3 with Composition API)
- **State Management**: Pinia
- **Styling**: Stylus
- **UI Libraries**: 
  - TanStack Table (table view)
  - Interact.js (draggable bubble view)
  - GSAP (animations)
- **Storage for caching**: Dexie (IndexedDB wrapper)

### Backend

- **Framework**: Django 5.2 LTS + Django REST Framework (Python 3.11+ compatible; LTS/security status verified)
- **Database**: PostgreSQL 16
- **Vector Database**: Weaviate 1.24.7 (with img2vec-neural ResNet50)
- **Storage**: 
  - Arweave (decentralized image storage)
  - AWS S3 (via django-storages, optional)
- **Image Processing**: Pillow
- **Server**: Gunicorn
- **Containerization**: Docker & Docker Compose

## Project Structure

```
backend/
├── artists/              # Main Django app
│   ├── models.py         # Artist & Artwork models
│   ├── views.py          # API endpoints
│   ├── serializers.py    # DRF serializers
│   ├── weaviate/         # AI vector search integration
│   ├── admin.py          # Custom admin with Arweave upload
│   └── tests/            # Test suite
├── artist_registry/      # Django project settings
├── docker-compose.yml    # PostgreSQL + Weaviate services
└── entrypoint.sh         # Production entrypoint

frontend/
├── pages/index.vue       # Main application page
├── components/           # Vue components
│   ├── Artist.vue        # Artist card component
│   ├── ArtistModal.vue   # Artist detail modal
│   ├── ArtistsTable.vue  # Table view component
│   ├── Filter.vue        # Filter controls
│   └── SearchImageByAI.vue # AI image search (in development)
├── J/                    # Pinia stores
│   ├── useArtistsStore.ts
│   ├── useFilterStore.ts
│   └── useSortStore.ts
└── services/idb.ts       # IndexedDB caching via Dexie
```

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Poetry (Python package manager)
- Yarn 4.1.0

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

4. Set up environment variables:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your local settings
   ```

5. Start Docker services (PostgreSQL and Weaviate):
   ```bash
   docker compose up -d
   ```

6. Run database migrations:
   ```bash
   export DJANGO_SETTINGS_MODULE=artist_registry.settings
   python3 manage.py migrate
   ```

7. Create superuser (optional):
   ```bash
   python3 manage.py createsuperuser
   ```

8. Start development server:
   ```bash
   python3 manage.py runserver
   ```

**Quick start command** (combines steps 5-8):
```bash
docker compose up -d && source venv/bin/activate && export DJANGO_SETTINGS_MODULE=artist_registry.settings && python3 manage.py runserver
```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   yarn install
   ```

3. Set up environment variables:
   Create a `.env` file with:
   ```
   DJANGO_SERVER_URL=http://localhost:8000
   ```

4. Start development server:
   ```bash
   yarn dev
   # or
   yarn d
   ```

## Database Management

### Local Development

**Access PostgreSQL:**
```bash
docker exec -it backend-db-1 psql -U postgres
```

**Create database dump:**
```bash
docker exec -i backend-db-1 pg_dump -U postgres art_db -Ft > dump_$(date +%d-%m-%Y"_"%H_%M_%S).tar
```

**Recreate database from dump:**
```bash
docker exec -it backend-db-1 dropdb -U postgres art_db && \
docker exec -it backend-db-1 createdb -U postgres art_db && \
cat <dump_file>.tar | docker exec -i backend-db-1 pg_restore -U postgres -d art_db
```

**Drop and recreate database:**
```bash
docker exec -it backend-db-1 psql -U postgres
DROP DATABASE art_db;
CREATE DATABASE art_db;
```

## Weaviate

Weaviate runs in Docker with the `img2vec-neural` module (ResNet50) for image similarity search.

**Test Weaviate connection:**
```bash
curl -X POST \
  'http://localhost:8080/v1/graphql' \
  -H 'Content-Type: application/json' \
  -d '{"query":"{ Aggregate { Artworks { meta { count } } } }"}'
```

## API Endpoints

- `GET /artists/` - List all artists with nested artworks
- `POST /artists/upload-to-arweave/<id>/` - Upload artist image to Arweave
- `GET /artists/search-artworks-by-image-url/` - AI similarity search by image URL *(integration in development)*
- `POST /artists/search-artworks-by-image-data/` - AI search with uploaded image file *(integration in development)*
- `GET /artists/search-authors-by-image-url/` - Search for similar artists by image URL *(integration in development)*

## Architecture Highlights

### Dual View System
- **Bubble View**: Interactive draggable artist cards using Interact.js
- **Table View**: Traditional sortable table using TanStack Table


### Arweave Integration
- Images uploaded to Arweave via Django admin panel (auto-upload on save)
- URLs stored in Artist/Artwork models

### Client-Side Caching
- IndexedDB via Dexie stores image blobs locally
- `BaseImage.vue` component handles caching and fallback images

### State Management
- `useArtistsStore`: Full artist dataset + filtered view
- `useFilterStore`: Text search, range filtering (birth year), gender, media type
- `useSortStore`: Sorting by name, birth year, auction turnover
- All filtering/sorting happens client-side on the full dataset


## Deployment

### Backend

Deployed on Railway. See [`backend/DEPLOYMENT.md`](backend/DEPLOYMENT.md) for instructions.

**Quick deploy:**
```bash
railway login
railway link
railway up
```

### Frontend

Deployed on Railway. See [`frontend/DEPLOYMENT.md`](frontend/DEPLOYMENT.md) for instructions.

**Quick deploy:**
```bash
railway login
railway link
railway up
```

## In Development

### AI-Powered Image Search

Search for similar artworks and artists using Weaviate vector database with ResNet50 image embeddings.

**Current Status:**
- ✅ Backend infrastructure implemented (Weaviate with img2vec-neural ResNet50)
- ✅ API endpoints functional (`/artists/search-artworks-by-image-url/`, `/artists/search-artworks-by-image-data/`, `/artists/search-authors-by-image-url/`)
- ✅ Similar artists pre-computed and stored in `similar_authors_postgres_ids` field
- ⚠️ UI integration incomplete - requires further development, testing, and debugging
- ⚠️ `SearchImageByAI.vue` component exists but needs completion

## License

MIT License - see LICENSE file
