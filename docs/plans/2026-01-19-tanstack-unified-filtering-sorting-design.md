# TanStack Unified Filtering & Sorting Design

## Overview

Refactor frontend filtering and sorting to use TanStack Table as the single source of truth, replacing the current Pinia-based approach with separate stores.

## Goals

- **Scalability**: Optimized for 1k-10k+ artists
- **Maintainability**: Single filtering/sorting system instead of three separate stores
- **Performance**: TanStack's memoized filtering/sorting vs manual array operations

## Architecture

```
                    ┌─────────────────────────┐
                    │   artistsAll (Pinia)    │  ← Source data only
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │   useArtistsTable       │  ← TanStack Table composable
                    │   - filtering           │
                    │   - sorting             │
                    │   - position calc       │
                    └───────────┬─────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
   ┌──────────▼──────┐  ┌───────▼───────┐  ┌─────▼─────┐
   │ Bubble View     │  │ Table View    │  │ Filter/   │
   │ (positions)     │  │ (virtualized) │  │ Sort UI   │
   └─────────────────┘  └───────────────┘  └───────────┘
```

## New Composable: useArtistsTable.ts

Location: `frontend/composables/useArtistsTable.ts`

### Core Structure

```typescript
import {
  useVueTable,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  createColumnHelper,
  type ColumnFiltersState,
  type SortingState,
} from '@tanstack/vue-table'
import { useArtistsStore, type Artist } from '~/J/useArtistsStore'

// Enums (moved from old stores)
export enum FilterOption { NAME, BORN, GENDER, AUCTIONS_TURNOVER_2023_H1_USD, MEDIA_TYPE }
export enum FilterType { SEARCH = 'SEARCH', RANGE = 'RANGE', SELECTION = 'SELECTION', SELECTION_TEXT = 'SELECTION_TEXT' }
export enum SortOption { FIRSTNAME, SURNAME, BORN, GENDER, AUCTIONS_TURNOVER_2023_H1_USD }
export enum SortDirection { ASC, DESC }
export enum GenderOptionEnum { NON_BINARY = "NON_BINARY", MAN = "MAN", WOMAN = "WOMAN" }
export enum MediaTypeOptionEnum { PAINTING = "PAINTING", NFT = "NFT", DIGITAL = "DIGITAL", SCULPTURE = "SCULPTURE" }

export const useArtistsTable = () => {
  const artistsStore = useArtistsStore()

  // TanStack state
  const columnFilters = ref<ColumnFiltersState>([])
  const globalFilter = ref('')
  const sorting = ref<SortingState>([])

  // Table instance
  const table = useVueTable({
    get data() { return artistsStore.artistsAll },
    columns,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    state: {
      get columnFilters() { return columnFilters.value },
      get globalFilter() { return globalFilter.value },
      get sorting() { return sorting.value },
    },
    onColumnFiltersChange: (updater) => {
      columnFilters.value = typeof updater === 'function'
        ? updater(columnFilters.value)
        : updater
    },
    onSortingChange: (updater) => {
      sorting.value = typeof updater === 'function'
        ? updater(sorting.value)
        : updater
    },
  })

  // Filtered + sorted artists
  const filteredArtists = computed(() =>
    table.getRowModel().rows.map(row => row.original)
  )

  // Artists with calculated positions for Bubble View
  const artistsWithPositions = computed(() =>
    calculatePositions(filteredArtists.value, currentSortField.value)
  )

  return {
    table,
    filteredArtists,
    artistsWithPositions,
    // Filter methods
    setNameFilter,
    setBornRangeFilter,
    setGenderFilter,
    setMediaTypeFilter,
    removeFilters,
    // Sort methods
    setSort,
    activeSort,
    // State for UI binding
    filters: { textToSearch: globalFilter, rangeFrom, rangeTo, selectedGenders, selectedMedia },
    // Enums & options
    FilterOption, FilterType, SortOption, SortDirection,
    genderOptions, mediaTypeOptions,
  }
}
```

### Column Definitions with Custom Filters

```typescript
const columnHelper = createColumnHelper<Artist>()

const columns = [
  columnHelper.accessor('name', {
    filterFn: 'includesString',
  }),

  columnHelper.accessor('born', {
    filterFn: (row, columnId, filterValue: { from?: number; to?: number }) => {
      const born = row.getValue<number>(columnId)
      if (filterValue.from && born < filterValue.from) return false
      if (filterValue.to && born > filterValue.to) return false
      return true
    },
  }),

  columnHelper.accessor('gender', {
    filterFn: (row, columnId, filterValue: GenderOptionEnum[]) => {
      if (!filterValue.length) return true
      const gender = row.getValue<string>(columnId)
      return filterValue.some(g => {
        if (g === GenderOptionEnum.NON_BINARY && gender === 'N') return true
        if (g === GenderOptionEnum.WOMAN && gender === 'W') return true
        if (g === GenderOptionEnum.MAN && gender === 'M') return true
        return false
      })
    },
  }),

  columnHelper.accessor('media_types', {
    filterFn: (row, columnId, filterValue: MediaTypeOptionEnum[]) => {
      if (!filterValue.length) return true
      const mediaTypes = row.getValue<string[]>(columnId)
      return filterValue.some(m => mediaTypes.includes(m.toLowerCase()))
    },
  }),

  // ... other columns for table display
]
```

### Filter Methods

```typescript
const setNameFilter = (text: string) => {
  globalFilter.value = text
}

const setBornRangeFilter = (from: number | null, to: number | null) => {
  const newFilters = columnFilters.value.filter(f => f.id !== 'born')
  if (from !== null || to !== null) {
    newFilters.push({ id: 'born', value: { from, to } })
  }
  columnFilters.value = newFilters
}

const setGenderFilter = (genders: GenderOptionEnum[]) => {
  const newFilters = columnFilters.value.filter(f => f.id !== 'gender')
  if (genders.length) {
    newFilters.push({ id: 'gender', value: genders })
  }
  columnFilters.value = newFilters
}

const setMediaTypeFilter = (mediaTypes: MediaTypeOptionEnum[]) => {
  const newFilters = columnFilters.value.filter(f => f.id !== 'media_types')
  if (mediaTypes.length) {
    newFilters.push({ id: 'media_types', value: mediaTypes })
  }
  columnFilters.value = newFilters
}

const removeFilters = () => {
  columnFilters.value = []
  globalFilter.value = ''
}
```

### Sort Methods

```typescript
const sortOptionToColumnId = (option: SortOption): string => {
  const map: Record<SortOption, string> = {
    [SortOption.FIRSTNAME]: 'firstname',
    [SortOption.SURNAME]: 'surname',
    [SortOption.BORN]: 'born',
    [SortOption.GENDER]: 'gender',
    [SortOption.AUCTIONS_TURNOVER_2023_H1_USD]: 'auctions_turnover_2023_h1_USD',
  }
  return map[option]
}

const setSort = (field: SortOption) => {
  const columnId = sortOptionToColumnId(field)
  const currentSort = sorting.value[0]
  const isCurrentField = currentSort?.id === columnId
  const newDesc = isCurrentField ? !currentSort.desc : false

  sorting.value = [{ id: columnId, desc: newDesc }]
}

const activeSort = computed(() => ({
  field: sorting.value[0]?.id ?? null,
  direction: sorting.value[0]?.desc ? SortDirection.DESC : SortDirection.ASC,
}))

const currentSortField = computed(() => sorting.value[0]?.id ?? null)
```

### Position Calculation

```typescript
const calculatePositions = (
  artists: Artist[],
  sortField: string | null
): (Artist & { calculatedY: number })[] => {
  const INITIAL_Y = 200
  const SPACING = 120

  let topPosition = INITIAL_Y

  return artists.map((artist, index) => {
    if (index === 0) {
      return { ...artist, calculatedY: topPosition }
    }

    const prevArtist = artists[index - 1]
    const hasSameValue = sortField
      && prevArtist[sortField as keyof Artist] === artist[sortField as keyof Artist]

    if (!hasSameValue) {
      topPosition += SPACING
    }

    return { ...artist, calculatedY: topPosition }
  })
}
```

## File Changes

### Files to CREATE

| File | Purpose |
|------|---------|
| `composables/useArtistsTable.ts` | New unified TanStack composable |

### Files to DELETE

| File | Reason |
|------|--------|
| `J/useFilterStore.ts` | Logic moves to useArtistsTable |
| `J/useSortStore.ts` | Logic moves to useArtistsTable |
| `composables/useArtistArrangement.ts` | Replaced by computed positions |

### Files to MODIFY

| File | Changes |
|------|---------|
| `J/useArtistsStore.ts` | Remove `artists` ref, keep only `artistsAll` |
| `components/artists-table/ArtistsTable.vue` | Import table from useArtistsTable |
| `pages/index.vue` | Use artistsWithPositions for Bubble View |
| `components/Artist.vue` | Use calculatedY for position |
| `components/Filter.vue` | Use useArtistsTable instead of useFilterStore |
| `components/filter/Option.vue` | Use useArtistsTable instead of useFilterStore |
| `components/Sort.vue` | Use useArtistsTable instead of useSortStore |
| `components/sort/Option.vue` | Use useArtistsTable instead of useSortStore |

## Migration Notes

### Bubble View

- Keep current DOM-based rendering for now
- Use `artistsWithPositions` computed property
- If performance becomes an issue at scale, disable Bubble View for large datasets

### Backward Compatibility

- Types and enums exported from useArtistsTable maintain same names
- Component APIs stay the same, only import source changes

### Position Handling

- Positions are computed from sort order, not stored on artist objects
- Drag positions still stored in artistsStore for persistence
- calculatedY used as initial position, drag overrides it

## Testing Checklist

- [ ] Text search filters artists in both views
- [ ] Born range filter works with min/max
- [ ] Gender multi-select filter works
- [ ] Media type multi-select filter works
- [ ] All sort options work (name, born, auctions)
- [ ] Sort direction toggles correctly
- [ ] Clear filters resets all filters
- [ ] Bubble View positions update on sort
- [ ] Table View virtualization still works
- [ ] Dragging artists still works in Bubble View
