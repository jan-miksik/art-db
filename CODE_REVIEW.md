# Code Review: a-db Project

A comprehensive code review of the art database application covering security, performance, code quality, and best practices.

**Project:** Artist Registry (Django + Nuxt 3)
**Date:** 2026-01-13
**Reviewer:** AI Code Review (Updated)

---

## Executive Summary

| Severity | Backend | Frontend | Total |
|----------|---------|----------|-------|
| CRITICAL | 7 | 3 | 10 |
| HIGH | 5 | 6 | 11 |
| MEDIUM | 12 | 8 | 20 |
| LOW | 6 | 5 | 11 |

**Key concerns:**
1. **Security:** Hardcoded secrets, DEBUG=True, CORS misconfiguration, no authentication, exposed wallet
2. **Memory leaks:** IntersectionObserver and interact.js not cleaned up in frontend
3. **Performance:** N+1 queries, missing indexes, expensive watchers
4. **Type safety:** Extensive use of `any` type in frontend

---

## Table of Contents
- [Backend (Django)](#backend-django)
  - [Critical Security Issues](#critical-security-issues)
  - [Performance Issues](#backend-performance-issues)
  - [Error Handling](#backend-error-handling)
  - [Code Quality](#backend-code-quality)
  - [API Design](#api-design)
  - [Database Model Issues](#database-model-issues)
- [Frontend (Nuxt/Vue)](#frontend-nuxtvue)
  - [Memory Leaks](#memory-leaks)
  - [State Management](#state-management)
  - [Performance Issues](#frontend-performance-issues)
  - [Type Safety](#type-safety)
  - [Accessibility](#accessibility)
  - [Code Duplication](#code-duplication)
- [Priority Action Items](#priority-action-items)
- [Quick Wins](#quick-wins)

---

## Backend (Django)

### Critical Security Issues

#### 1. Hardcoded Secret Key
**File:** `backend/artist_registry/settings.py:29`
```python
SECRET_KEY = 'django-insecure-bxp#bec1r2p-=mos4@c1(m2=9tvp&#6a6dm=4c^$cs@$c+z&yv'
```
**Risk:** Session hijacking, CSRF token forgery, password reset token compromise
**Fix:**
```python
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY environment variable required")
```

---

#### 2. DEBUG = True in Production
**File:** `backend/artist_registry/settings.py:32`
```python
DEBUG = True
```
**Risk:** Exposes sensitive information in error pages (database queries, file paths, settings)
**Fix:**
```python
DEBUG = os.getenv('DEBUG', 'False') == 'True'
```

---

#### 3. CORS_ALLOW_ALL_ORIGINS = True
**File:** `backend/artist_registry/settings.py:65`
```python
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://0.0.0.0",
    'http://*'  # Invalid pattern
]
```
**Risk:** Any website can make cross-origin API requests, enables CSRF attacks
**Fix:** Whitelist specific domains only, remove wildcards

---

#### 4. No Authentication on API Endpoints
**File:** `backend/artists/views.py`

All endpoints are publicly accessible without authentication:
- `artists_endpoint` (line 20)
- `search_artworks_by_image_data` (line 92)
- `search_artworks_by_image_url` (line 118)
- `search_authors_by_image_data` (line 40)
- `search_authors_by_image_url` (line 66)

**Fix:** Add DRF authentication
```python
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def artists_endpoint(request):
    ...
```

---

#### 5. CSRF Exemptions on All POST Endpoints
**File:** `backend/artists/urls.py:8-12`
```python
path('upload-to-arweave/<int:pk>/', csrf_exempt(views.upload_to_arweave_view)),
path('search-artworks-by-image-url/', csrf_exempt(views.search_artworks_by_image_url)),
path('search-artworks-by-image-data/', csrf_exempt(views.search_artworks_by_image_data)),
path('search-authors-by-image-data/', csrf_exempt(views.search_authors_by_image_data)),
path('search-authors-by-image-url/', csrf_exempt(views.search_authors_by_image_url)),
```
**Risk:** Cross-site request forgery attacks combined with CORS_ALLOW_ALL = complete API exposure
**Fix:** Remove `csrf_exempt`, implement proper token-based auth (JWT, DRF Token)

---

#### 6. Exposed Arweave Wallet
**File:** `backend/artists/admin.py:82, 104, 157`
```python
wallet_path = os.path.join(settings.MEDIA_ROOT, 'arweave_wallet.json')
```
**Risk:** Wallet theft if `/media/` is publicly accessible. Anyone with wallet access can drain funds.
**Fix:**
- Store outside web root
- Use environment variable for path: `os.getenv('ARWEAVE_WALLET_PATH')`
- Restrict file permissions to 0600

---

#### 7. SSRF via Unvalidated Image URLs
**File:** `backend/artists/weaviate/weaviate.py:53-62`
```python
def url_to_base64(url):
    response = requests.get(url)  # No validation, no timeout
    response.raise_for_status()
```
**Risk:** Server-side request forgery - can access internal services (localhost, 192.168.x.x)
**Fix:**
```python
def url_to_base64(url, timeout=10):
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        raise ValueError("Invalid URL scheme")
    if parsed.hostname in ('localhost', '127.0.0.1'):
        raise ValueError("Cannot access localhost")
    if parsed.hostname and parsed.hostname.startswith('192.168'):
        raise ValueError("Cannot access private network")

    response = requests.get(url, timeout=timeout, verify=True)
    content_type = response.headers.get('content-type', '')
    if not content_type.startswith('image/'):
        raise ValueError("URL does not point to an image")
    return base64.b64encode(response.content).decode()
```

---

### Backend Performance Issues

#### 8. N+1 Query Problem
**Files:** `backend/artists/views.py:50-59, 72-83, 102-111, 125-136`
```python
for image in similar_images.objects:
    artwork = Artwork.objects.filter(id=image.properties['artwork_psql_id']).first()
    author = Artist.objects.filter(id=image.properties['author_psql_id']).first()
```
**Impact:** 200 queries for 100 images
**Fix:** Batch fetch with `filter(id__in=ids)`
```python
artwork_ids = [img.properties['artwork_psql_id'] for img in similar_images.objects]
author_ids = [img.properties['author_psql_id'] for img in similar_images.objects]
artworks = {a.id: a for a in Artwork.objects.filter(id__in=artwork_ids)}
authors = {a.id: a for a in Artist.objects.filter(id__in=author_ids)}
```

---

#### 9. Missing Database Indexes
**File:** `backend/artists/models.py`
```python
profile_image_weaviate_id = models.CharField(max_length=200, blank=True)  # No index
picture_image_weaviate_id = models.CharField(max_length=200, blank=True)  # No index
```
**Fix:** Add `db_index=True` to frequently queried fields

---

#### 10. Weaviate Client Connection Leaks
**File:** `backend/artists/weaviate/weaviate.py:158, 234, 252, 294`

Context manager exists at line 15-24 but not used consistently:
```python
def search_similar_authors_ids_by_base64(image_data_base64, limit=2):
    weaviate_client = weaviate.connect_to_local()
    # ... operations ...
    weaviate_client.close()  # Not reached on exception
```
**Fix:** Use context manager `get_weaviate_client()` consistently with `with` statement

---

### Backend Error Handling

#### 11. Missing Error Handling in File Upload
**File:** `backend/artists/views.py:26-36`
```python
def upload_to_arweave_view(request, pk):
    file = request.FILES.get('file')
    if file:
        file_path = file.temporary_file_path()  # Fails for in-memory files (<2.5MB)
        arweave_url = upload_to_arweave(file_path)  # No try/except
```
**Fix:** Handle exceptions, validate file type/size, check permissions

---

#### 12. Bare Exception Handlers
**File:** `backend/artists/weaviate/weaviate.py:86-87`
```python
except:  # Catches SystemExit, KeyboardInterrupt
    return False
```
**Fix:** Catch specific exceptions
```python
except (weaviate.exceptions.WeaviateException, Exception) as e:
    logger.warning(f"Failed to check object {obj_uuid}: {e}")
    return False
```

---

#### 13. No Validation of Weaviate Response Properties
**File:** `backend/artists/views.py:50-52`
```python
for image in similar_images.objects:
    artwork = Artwork.objects.filter(id=image.properties['artwork_psql_id']).first()
```
**Risk:** KeyError if `properties` doesn't have expected keys
**Fix:** Use `.get()` with validation and handle missing data gracefully

---

### Backend Code Quality

#### 14. Print Statements Instead of Logging
**Files:** `backend/artists/admin.py:87, 110, 117`, `backend/artists/weaviate/weaviate.py:101`
```python
print("save_related artwork to db")  # admin.py:87
print("[[[[[ add_image_to_weaviete ]]]]]")  # weaviate.py:101
```
**Fix:** Use Python logging module
```python
import logging
logger = logging.getLogger(__name__)
logger.debug("Saving related artworks to database")
```

---

#### 15. Typo in Function Name
**File:** `backend/artists/weaviate/weaviate.py`
```python
def add_image_to_weaviete(...)  # Should be "weaviate"
```
Used 6+ times throughout the file. Rename to `add_image_to_weaviate`.

---

#### 16. Large Monolithic Module
**File:** `backend/artists/weaviate/weaviate.py` (459 lines)

Mix of concerns. Split into:
```
weaviate/
  __init__.py
  client.py      # Connection management
  service.py     # Business logic
  queries.py     # Query functions
  exceptions.py  # Custom exceptions
```

---

#### 17. Commented Out / Dead Code
**File:** `backend/artists/weaviate/weaviate.py:65-74, 193-212, 215-227, 282-349`

Large blocks of commented code. Delete and rely on git history.

---

### API Design

#### 18. Inconsistent Response Format
```python
# Success - just data
Response(response_data)

# Error - dict with 'error' key
Response({'error': 'Image data not provided'}, status=400)
```
**Fix:** Standardize response wrapper
```python
return Response({
    'success': True/False,
    'data': {...},
    'error': None or message,
})
```

---

#### 19. Duplicate Endpoint Logic
**File:** `backend/artists/views.py:66-85 vs 118-138`

`search_authors_by_image_url` and `search_artworks_by_image_url` share nearly identical code.
**Fix:** Extract common logic into helper function

---

#### 20. Missing Request Validation
**File:** `backend/artists/views.py:42, 68, 94, 120`
```python
limit = int(request.data.get('limit', 2))  # ValueError on non-integer, no bounds
```
**Fix:** Validate with bounds
```python
def get_validated_limit(data, key, default=2, min_val=1, max_val=100):
    try:
        limit = int(data.get(key, default))
        return max(min_val, min(limit, max_val))
    except (ValueError, TypeError):
        return default
```

---

### Database Model Issues

#### 21. Weak Field Naming
**File:** `backend/artists/models.py:49-50`
```python
sizeY = models.IntegerField(null=True, blank=True)  # Should be snake_case
sizeX = models.IntegerField(null=True, blank=True)
```
**Fix:** Rename to `height`, `width`

---

#### 22. Missing Field Validation
**File:** `backend/artists/models.py`
```python
year = models.IntegerField(null=True, blank=True)  # No min/max
sizeY = models.IntegerField(null=True, blank=True)  # Could be negative
auctions_turnover_2023_h1_USD = models.DecimalField(...)  # Could be negative
```
**Fix:** Add validators
```python
from django.core.validators import MinValueValidator, MaxValueValidator
year = models.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(2100)])
```

---

#### 23. Missing Security Settings for Production
**File:** `backend/artist_registry/settings.py`

Missing:
```python
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
```

---

## Frontend (Nuxt/Vue)

### Memory Leaks

#### 24. IntersectionObserver Not Disconnected
**File:** `frontend/components/BaseImage.vue:106-127`
```typescript
onMounted(async () => {
  const observer = new IntersectionObserver(...)
  observer.observe(fullImageRef.value)
})

onUnmounted(() => {
  // Missing: observer.disconnect()
})
```
**Fix:** Store observer reference and call `disconnect()` in onUnmounted
```typescript
let observer: IntersectionObserver | null = null

onMounted(() => {
  observer = new IntersectionObserver(...)
  observer.observe(fullImageRef.value)
})

onUnmounted(() => {
  observer?.disconnect()
  fullImageRef.value?.removeEventListener('load', loadedFullImage)
})
```

---

#### 25. interact.js Not Cleaned Up
**File:** `frontend/components/Artist.vue:79-103`
```typescript
onMounted(() => {
  interact(artistRef.value as any)
    .draggable({ ... })
    .resizable({ ... })
})
// No cleanup in onUnmounted
```
**Fix:** Call `interact(artistRef.value).unset()` in onUnmounted

---

#### 26. Document Event Listeners Not Cleaned
**File:** `frontend/components/Filter.vue:62-68`

Click outside handler is commented out but the pattern in Sort.vue shows the issue - if document listeners aren't properly cleaned up, they persist.

---

### State Management

#### 27. Direct Store Mutation Outside Actions
**File:** `frontend/pages/index.vue:65-68`
```typescript
useArtistsStore().artistsAll = response.data;
useArtistsStore().artists = response.data;
useArtistsStore().artists.forEach((artist: any) => {
  artist.position = randomizePosition();
});
```
**Problems:**
- Mutates store state directly
- Mutates API response data
- Inconsistent store access pattern (both direct calls and assigned variables)

**Fix:** Create store actions for state changes

---

#### 28. Duplicate hasFilters Condition
**File:** `frontend/J/useFilterStore.ts:62`
```typescript
const hasFilters = computed(() =>
    rangeFrom.value ||
    rangeTo.value ||
    textToSearch.value ||
    isFilterByGender.value ||
    isShowSimilarAuthors.value ||
    isFilterByMediaType.value ||
    isFilterByMediaType.value  // <-- DUPLICATE LINE
)
```
**Fix:** Remove duplicate line

---

#### 29. Minimal Store with No Actions
**File:** `frontend/J/useArtistsStore.ts:26-33`
```typescript
export const useArtistsStore = defineStore('artists', () => {
  const artists = ref<Artist[]>([])
  const artistsAll = ref<Artist[]>([])
  return { artists, artistsAll }
})
```
Store is just a data container with no mutations/actions. Should have proper actions for fetching, updating, filtering.

---

### Frontend Performance Issues

#### 30. Blocking API Without Loading State
**File:** `frontend/pages/index.vue:62-72`
```typescript
onMounted(async () => {
  axios.get(...)
    .then((response) => {...})
    .catch((error) => console.error("Error:", error));
})
```
**Problems:**
- No loading indicator
- No timeout
- Data assigned twice (lines 65-66)
- Error only logged, no user feedback

---

#### 31. Computed Generates New Random Values Every Render
**File:** `frontend/components/Artist.vue:76`
```typescript
const randomizedRotation = computed(() => randomizeRotation())
```
**Problem:** Generates new random value on every render
**Fix:** Calculate once in onMounted, store in ref

---

#### 32. Expensive Deep Watch
**File:** `frontend/components/ArtistsTable.vue:159-161`
```typescript
watch(() => data.value, () => {
  table.getRowModel().rows
}, {deep: true})
```
**Problem:** Deep watching array is expensive, callback does nothing useful

---

#### 33. Artificial Delays in Store Actions
**File:** `frontend/J/useFilterStore.ts:121-122, 172, 214`
```typescript
const sleep = async (ms: number) => {...}
await sleep(1000)
```
**Problem:** Arbitrary 1s delays degrade UX. Remove or reduce.

---

### Type Safety

#### 34. Extensive Use of `any` Type

| File | Line | Code |
|------|------|------|
| Artist.vue | 79 | `interact(artistRef.value as any)` |
| pages/index.vue | 67 | `artists.forEach((artist: any)` |
| BaseImage.vue | 24 | `externalCssClass?: any` |
| ArtistModal.vue | 98 | `const onSwiper = (swiper: any)` |
| Filter.vue | 56 | `handleClickOutside = (event: any)` |

**Fix:** Add proper types from libraries (Swiper types, Event types, Interactable, etc.)

---

### Accessibility

#### 35. Non-Semantic Interactive Elements

| File | Line | Issue |
|------|------|-------|
| pages/index.vue | 8 | `<div @click>` instead of `<button>` |
| Artist.vue | 6 | Clickable div without keyboard support |
| Filter.vue | 9 | Toggle without ARIA attributes |
| Sort.vue | 4 | Toggle without ARIA attributes |

**Fix:** Use `<button>` elements, add `aria-expanded`, `aria-controls`, keyboard handlers

---

#### 36. Missing Labels
**File:** `frontend/components/Filter/Option.vue:4`
```html
<input v-model="textToSearch" placeholder=""/>
```
**Problem:** No associated `<label>` element
**Fix:** Add proper labeling

---

#### 37. No Focus Management in Modal
**File:** `frontend/components/ArtistModal.vue`

Modal opens but no focus trap. Keyboard users can tab outside modal.
**Fix:** Implement focus trap using a composable or library

---

### Code Duplication

#### 38. Duplicated Functions

| Function | Locations |
|----------|-----------|
| `randomRange()` | pages/index.vue:40-42, Artist.vue:67-69 |
| `reArrangeSortedArtists()` | useFilterStore.ts:95-119, useSortStore.ts:32-56 (identical!) |
| `sleep()` | useFilterStore.ts:121-123, useSortStore.ts:28-30 |

**Fix:** Extract to `utils/` or composables

---

### Miscellaneous Frontend Issues

#### 39. Debug Console.log in Production Code
**File:** `frontend/components/ArtistsTable.vue:147`
```typescript
console.log('data', data.value)
```
**Fix:** Remove

---

#### 40. Unconventional Store Directory Name
**File:** `frontend/nuxt.config.ts:14`
```typescript
pinia: {
  storesDirs: ['./J/**', ],
},
```
**Problem:** `J/` is unconventional
**Fix:** Rename to `stores/`

---

#### 41. Hardcoded Z-Index Values
Multiple files use extremely high z-index:
```stylus
z-index: 10000000000
```
Files: pages/index.vue:95, ArtistModal.vue:136

**Fix:** Use CSS custom properties or a z-index scale

---

#### 42. Mouse Action Detector Logic May Be Inverted
**File:** `frontend/J/useMouseActionDetector.ts:12-14`
```typescript
const mouseDownHandler = () => {
  isDragging.value = false;  // Should this be true?
};
```
Verify this is intentional.

---

## Priority Action Items

### Immediate (Before Production)

| # | Issue | Severity | Effort |
|---|-------|----------|--------|
| 1 | Generate new SECRET_KEY from environment | CRITICAL | Low |
| 2 | Set DEBUG = False via env var | CRITICAL | Low |
| 3 | Remove CORS_ALLOW_ALL_ORIGINS | CRITICAL | Low |
| 4 | Add authentication to API endpoints | CRITICAL | Medium |
| 5 | Remove CSRF exemptions | CRITICAL | Medium |
| 6 | Move Arweave wallet outside web root | CRITICAL | Medium |
| 7 | Add URL validation for SSRF protection | HIGH | Medium |
| 8 | Fix IntersectionObserver memory leak | CRITICAL | Low |
| 9 | Fix interact.js cleanup | CRITICAL | Low |

### Short Term (Next Sprint)

| # | Issue | Severity | Effort |
|---|-------|----------|--------|
| 10 | Fix N+1 queries | HIGH | Medium |
| 11 | Add database indexes | HIGH | Low |
| 12 | Fix Weaviate connection management | HIGH | Low |
| 13 | Replace print() with logging | MEDIUM | Low |
| 14 | Add proper TypeScript types | HIGH | Medium |
| 15 | Fix accessibility issues (buttons, ARIA) | HIGH | Medium |
| 16 | Add loading states and error handling | HIGH | Medium |

### Medium Term (Next Month)

| # | Issue | Severity | Effort |
|---|-------|----------|--------|
| 17 | Add field validation to models | MEDIUM | Low |
| 18 | Refactor weaviate module into sub-modules | MEDIUM | High |
| 19 | Add API documentation | MEDIUM | Medium |
| 20 | Extract duplicate code to utilities | MEDIUM | Medium |
| 21 | Implement consistent response format | MEDIUM | Low |
| 22 | Create proper store actions | MEDIUM | Medium |
| 23 | Add production security settings | HIGH | Low |

### Long Term (Roadmap)

| # | Issue | Severity | Effort |
|---|-------|----------|--------|
| 24 | Add caching layer (Redis) | MEDIUM | High |
| 25 | Implement async tasks (Celery) for Arweave | MEDIUM | High |
| 26 | Add comprehensive test suite | MEDIUM | High |
| 27 | Implement lazy loading for components | LOW | Medium |
| 28 | Add focus trap to modal | LOW | Low |

---

## Quick Wins

These can be fixed in under 30 minutes each:

1. **Add `db_index=True`** to weaviate_id fields in models.py
2. **Replace `print()` with `logger.debug()`** throughout backend
3. **Fix duplicate `isFilterByMediaType`** in useFilterStore.ts line 62
4. **Remove `console.log`** from ArtistsTable.vue line 147
5. **Add `observer.disconnect()`** in BaseImage.vue onUnmounted
6. **Extract `randomRange()`** to shared utility
7. **Remove commented code blocks** in weaviate.py
8. **Fix typo `weaviete` → `weaviate`** in function names
9. **Add timeout to `requests.get()`** calls in weaviate.py
10. **Rename `J/` directory** to `stores/`

---

## Summary

The application is functional but requires significant improvements in security, code quality, and architecture. The most critical issues are:

1. **Security vulnerabilities** - exposed secrets, no auth, SSRF risk
2. **Memory leaks** - observers and event listeners not cleaned up
3. **Performance** - N+1 queries, missing indexes
4. **Code quality** - type safety, error handling, code duplication

Address critical security issues immediately before any production deployment. The quick wins listed above provide easy improvements with minimal risk.
