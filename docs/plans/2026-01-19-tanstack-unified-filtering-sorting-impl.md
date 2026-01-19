# TanStack Unified Filtering & Sorting Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace separate Pinia filter/sort stores with a unified TanStack Table composable that handles filtering, sorting, and position calculation for both Table and Bubble views.

**Architecture:** Single `useArtistsTable` composable wraps TanStack Table with custom filter functions. Both views consume filtered/sorted data from this composable. Positions are computed reactively from sort order.

**Tech Stack:** Vue 3, TanStack Table v8, TanStack Virtual, Pinia, TypeScript

---

## Task 1: Create useArtistsTable Composable - Core Structure

**Files:**
- Create: `frontend/composables/useArtistsTable.ts`

**Step 1: Create the composable file with types and enums**

```typescript
// frontend/composables/useArtistsTable.ts
import { ref, computed } from 'vue'
import {
  useVueTable,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  createColumnHelper,
  type ColumnFiltersState,
  type SortingState,
  type FilterFn,
} from '@tanstack/vue-table'
import { useArtistsStore, type Artist } from '~/J/useArtistsStore'

// Icons (moved from useFilterStore)
import FluidSvg from '~/assets/fluid.svg'
import FemalePng from '~/assets/female.png'
import MalePng from '~/assets/male.png'

// Enums
export enum FilterOption {
  NAME,
  BORN,
  GENDER,
  AUCTIONS_TURNOVER_2023_H1_USD,
  MEDIA_TYPE,
}

export enum FilterType {
  SEARCH = 'SEARCH',
  RANGE = 'RANGE',
  SELECTION = 'SELECTION',
  SELECTION_TEXT = 'SELECTION_TEXT',
}

export enum SortOption {
  FIRSTNAME,
  SURNAME,
  BORN,
  GENDER,
  AUCTIONS_TURNOVER_2023_H1_USD,
}

export enum SortDirection {
  ASC = 'ASC',
  DESC = 'DESC',
}

export enum GenderOptionEnum {
  NON_BINARY = 'NON_BINARY',
  MAN = 'MAN',
  WOMAN = 'WOMAN',
}

export enum MediaTypeOptionEnum {
  PAINTING = 'PAINTING',
  NFT = 'NFT',
  DIGITAL = 'DIGITAL',
  SCULPTURE = 'SCULPTURE',
}

export type SelectionOptionType<T> = {
  text?: string
  sign?: string
  enumValue: T
}

export type ArtistWithPosition = Artist & { calculatedY: number }
```

**Step 2: Verify file created**

Run: `ls -la frontend/composables/useArtistsTable.ts`
Expected: File exists

**Step 3: Commit**

```bash
git add frontend/composables/useArtistsTable.ts
git commit -m "feat: add useArtistsTable composable scaffold with types"
```

---

## Task 2: Add Column Definitions with Custom Filter Functions

**Files:**
- Modify: `frontend/composables/useArtistsTable.ts`

**Step 1: Add custom filter functions and column definitions**

Add after the type definitions:

```typescript
// Custom filter functions
const bornRangeFilter: FilterFn<Artist> = (row, columnId, filterValue: { from?: number | null; to?: number | null }) => {
  if (!filterValue) return true
  const born = row.getValue<number>(columnId)
  if (filterValue.from && born < filterValue.from) return false
  if (filterValue.to && born > filterValue.to) return false
  return true
}

const genderFilter: FilterFn<Artist> = (row, columnId, filterValue: GenderOptionEnum[]) => {
  if (!filterValue?.length) return true
  const gender = row.getValue<string>(columnId)
  return filterValue.some((g) => {
    if (g === GenderOptionEnum.NON_BINARY && gender === 'N') return true
    if (g === GenderOptionEnum.WOMAN && gender === 'W') return true
    if (g === GenderOptionEnum.MAN && gender === 'M') return true
    return false
  })
}

const mediaTypeFilter: FilterFn<Artist> = (row, columnId, filterValue: MediaTypeOptionEnum[]) => {
  if (!filterValue?.length) return true
  const mediaTypes = row.getValue<string[]>(columnId)
  return filterValue.some((m) => mediaTypes.includes(m.toLowerCase() as any))
}

// Column helper
const columnHelper = createColumnHelper<Artist>()

// Column definitions for filtering/sorting (not display - ArtistsTable has its own)
const filterColumns = [
  columnHelper.accessor('name', {}),
  columnHelper.accessor('firstname', {}),
  columnHelper.accessor('surname', {}),
  columnHelper.accessor('born', {
    filterFn: bornRangeFilter,
  }),
  columnHelper.accessor('gender', {
    filterFn: genderFilter,
  }),
  columnHelper.accessor('media_types', {
    filterFn: mediaTypeFilter,
  }),
  columnHelper.accessor('auctions_turnover_2023_h1_USD', {}),
  columnHelper.accessor('profile_image_url', {}),
  columnHelper.accessor('artworks', {}),
]
```

**Step 2: Commit**

```bash
git add frontend/composables/useArtistsTable.ts
git commit -m "feat: add TanStack column definitions with custom filter functions"
```

---

## Task 3: Add Position Calculation Function

**Files:**
- Modify: `frontend/composables/useArtistsTable.ts`

**Step 1: Add position calculation helper**

Add after column definitions:

```typescript
// Position calculation for Bubble View
const calculatePositions = (
  artists: Artist[],
  sortField: string | null
): ArtistWithPosition[] => {
  const INITIAL_Y = 200
  const SPACING = 120

  let topPosition = INITIAL_Y

  return artists.map((artist, index) => {
    if (index === 0) {
      return { ...artist, calculatedY: topPosition }
    }

    const prevArtist = artists[index - 1]
    let hasSameValue = false

    if (sortField && sortField in artist && sortField in prevArtist) {
      hasSameValue = prevArtist[sortField as keyof Artist] === artist[sortField as keyof Artist]
    }

    if (!hasSameValue) {
      topPosition += SPACING
    }

    return { ...artist, calculatedY: topPosition }
  })
}
```

**Step 2: Commit**

```bash
git add frontend/composables/useArtistsTable.ts
git commit -m "feat: add position calculation for Bubble View"
```

---

## Task 4: Implement the Main Composable Function

**Files:**
- Modify: `frontend/composables/useArtistsTable.ts`

**Step 1: Add the useArtistsTable composable export**

Add at the end of the file:

```typescript
// Options for UI
const genderOptions: SelectionOptionType<GenderOptionEnum>[] = [
  { sign: FluidSvg, enumValue: GenderOptionEnum.NON_BINARY },
  { sign: MalePng, enumValue: GenderOptionEnum.MAN },
  { sign: FemalePng, enumValue: GenderOptionEnum.WOMAN },
]

const mediaTypeOptions: SelectionOptionType<MediaTypeOptionEnum>[] = [
  { text: 'painting', enumValue: MediaTypeOptionEnum.PAINTING },
  { text: 'nft', enumValue: MediaTypeOptionEnum.NFT },
  { text: 'sculpture', enumValue: MediaTypeOptionEnum.SCULPTURE },
]

export const useArtistsTable = () => {
  const artistsStore = useArtistsStore()

  // TanStack state
  const columnFilters = ref<ColumnFiltersState>([])
  const globalFilter = ref('')
  const sorting = ref<SortingState>([])

  // UI-friendly filter state refs
  const rangeFrom = ref('')
  const rangeTo = ref('')
  const selectedGendersToShow = ref<SelectionOptionType<GenderOptionEnum>[]>([])
  const selectedMediaToShow = ref<SelectionOptionType<MediaTypeOptionEnum>[]>([])
  const isFilteringInProgress = ref(false)

  // Create table instance
  const table = useVueTable({
    get data() {
      return artistsStore.artistsAll
    },
    columns: filterColumns,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    globalFilterFn: 'includesString',
    state: {
      get columnFilters() {
        return columnFilters.value
      },
      get globalFilter() {
        return globalFilter.value
      },
      get sorting() {
        return sorting.value
      },
    },
    onColumnFiltersChange: (updater) => {
      columnFilters.value = typeof updater === 'function' ? updater(columnFilters.value) : updater
    },
    onGlobalFilterChange: (updater) => {
      globalFilter.value = typeof updater === 'function' ? updater(globalFilter.value) : updater
    },
    onSortingChange: (updater) => {
      sorting.value = typeof updater === 'function' ? updater(sorting.value) : updater
    },
  })

  // Computed: filtered + sorted artists
  const filteredArtists = computed(() => table.getRowModel().rows.map((row) => row.original))

  // Computed: current sort field
  const currentSortField = computed(() => sorting.value[0]?.id ?? null)

  // Computed: artists with calculated positions for Bubble View
  const artistsWithPositions = computed(() =>
    calculatePositions(filteredArtists.value, currentSortField.value)
  )

  // Computed: active sort state for UI
  const activeSort = computed(() => ({
    field: currentSortField.value,
    direction: sorting.value[0]?.desc ? SortDirection.DESC : SortDirection.ASC,
  }))

  // Computed: has any filters applied
  const hasFilters = computed(
    () =>
      globalFilter.value ||
      rangeFrom.value ||
      rangeTo.value ||
      selectedGendersToShow.value.length > 0 ||
      selectedMediaToShow.value.length > 0
  )

  return {
    // Table instance (for ArtistsTable.vue direct usage)
    table,
    // Filtered data
    filteredArtists,
    artistsWithPositions,
    // Sort state
    activeSort,
    currentSortField,
    // Filter state for UI binding
    textToSearch: globalFilter,
    rangeFrom,
    rangeTo,
    selectedGendersToShow,
    selectedMediaToShow,
    hasFilters,
    isFilteringInProgress,
    // Options
    genderOptions,
    mediaTypeOptions,
    // Enums
    FilterOption,
    FilterType,
    SortOption,
    SortDirection,
  }
}
```

**Step 2: Verify no TypeScript errors**

Run: `cd frontend && yarn nuxi typecheck 2>&1 | head -50`
Expected: No errors related to useArtistsTable.ts

**Step 3: Commit**

```bash
git add frontend/composables/useArtistsTable.ts
git commit -m "feat: implement useArtistsTable composable core"
```

---

## Task 5: Add Filter Methods

**Files:**
- Modify: `frontend/composables/useArtistsTable.ts`

**Step 1: Add filter methods inside useArtistsTable before the return statement**

```typescript
  // --- Filter Methods ---

  const updateColumnFilter = (columnId: string, value: unknown) => {
    const newFilters = columnFilters.value.filter((f) => f.id !== columnId)
    if (value !== null && value !== undefined) {
      newFilters.push({ id: columnId, value })
    }
    columnFilters.value = newFilters
  }

  const searchAndFilterByName = (whatToSearch: string) => {
    globalFilter.value = whatToSearch
  }

  const filterByBornInRange = (from: number | null, to: number | null) => {
    const hasFrom = from !== null && !isNaN(from)
    const hasTo = to !== null && !isNaN(to)

    rangeFrom.value = hasFrom ? String(from) : ''
    rangeTo.value = hasTo ? String(to) : ''

    if (hasFrom || hasTo) {
      updateColumnFilter('born', { from: hasFrom ? from : null, to: hasTo ? to : null })
    } else {
      updateColumnFilter('born', null)
    }
  }

  const filterByGender = (selectedGender?: SelectionOptionType<GenderOptionEnum>) => {
    if (!selectedGender) return

    const isSelected = selectedGendersToShow.value.some(
      (o) => o.enumValue === selectedGender.enumValue
    )

    if (isSelected) {
      selectedGendersToShow.value = selectedGendersToShow.value.filter(
        (o) => o.enumValue !== selectedGender.enumValue
      )
    } else {
      selectedGendersToShow.value = [...selectedGendersToShow.value, selectedGender]
    }

    const genderEnums = selectedGendersToShow.value.map((o) => o.enumValue)
    updateColumnFilter('gender', genderEnums.length ? genderEnums : null)
  }

  const filterByMediaType = (selectedMediaType?: SelectionOptionType<MediaTypeOptionEnum>) => {
    if (!selectedMediaType) return

    const isSelected = selectedMediaToShow.value.some(
      (o) => o.enumValue === selectedMediaType.enumValue
    )

    if (isSelected) {
      selectedMediaToShow.value = selectedMediaToShow.value.filter(
        (o) => o.enumValue !== selectedMediaType.enumValue
      )
    } else {
      selectedMediaToShow.value = [...selectedMediaToShow.value, selectedMediaType]
    }

    const mediaEnums = selectedMediaToShow.value.map((o) => o.enumValue)
    updateColumnFilter('media_types', mediaEnums.length ? mediaEnums : null)
  }

  const removeFilters = () => {
    columnFilters.value = []
    globalFilter.value = ''
    rangeFrom.value = ''
    rangeTo.value = ''
    selectedGendersToShow.value = []
    selectedMediaToShow.value = []
  }
```

**Step 2: Add filter methods to the return statement**

Update the return statement to include:

```typescript
  return {
    // ... existing exports ...
    // Filter methods
    searchAndFilterByName,
    filterByBornInRange,
    filterByGender,
    filterByMediaType,
    removeFilters,
  }
```

**Step 3: Commit**

```bash
git add frontend/composables/useArtistsTable.ts
git commit -m "feat: add filter methods to useArtistsTable"
```

---

## Task 6: Add Sort Methods

**Files:**
- Modify: `frontend/composables/useArtistsTable.ts`

**Step 1: Add sort methods inside useArtistsTable before the return statement**

```typescript
  // --- Sort Methods ---

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

  const columnIdToSortOption = (columnId: string | null): SortOption | null => {
    if (!columnId) return null
    const map: Record<string, SortOption> = {
      firstname: SortOption.FIRSTNAME,
      surname: SortOption.SURNAME,
      born: SortOption.BORN,
      gender: SortOption.GENDER,
      auctions_turnover_2023_h1_USD: SortOption.AUCTIONS_TURNOVER_2023_H1_USD,
    }
    return map[columnId] ?? null
  }

  const setSort = (field: SortOption) => {
    const columnId = sortOptionToColumnId(field)
    const currentSort = sorting.value[0]
    const isCurrentField = currentSort?.id === columnId

    // Toggle: ASC -> DESC -> ASC (same field) or start with ASC (new field)
    const newDesc = isCurrentField ? !currentSort.desc : false

    sorting.value = [{ id: columnId, desc: newDesc }]
  }

  const isSortingInProgress = ref(false)
```

**Step 2: Update activeSort computed and add to return statement**

Update activeSort to use SortOption:

```typescript
  const activeSort = computed(() => ({
    field: columnIdToSortOption(currentSortField.value),
    direction: sorting.value[0]?.desc ? SortDirection.DESC : SortDirection.ASC,
  }))
```

Add to return statement:

```typescript
  return {
    // ... existing exports ...
    // Sort methods
    setSort,
    isSortingInProgress,
  }
```

**Step 3: Commit**

```bash
git add frontend/composables/useArtistsTable.ts
git commit -m "feat: add sort methods to useArtistsTable"
```

---

## Task 7: Update ArtistsTable.vue to Use Shared Composable

**Files:**
- Modify: `frontend/components/artists-table/ArtistsTable.vue`

**Step 1: Update imports and use shared table**

Replace the script section:

```vue
<script setup lang="tsx">
import { computed, ref } from 'vue'
import { FlexRender } from '@tanstack/vue-table'
import { useVirtualizer } from '@tanstack/vue-virtual'

import BaseImage from '~/components/BaseImage.vue'
import useArtistModal from './../useArtistModal'
import type { Artist } from '~/J/useArtistsStore'
import { useArtistsTable } from '~/composables/useArtistsTable'

const { openArtistModal } = useArtistModal()
const openModal = (artist: Artist) => openArtistModal(artist)

// Use shared table from composable
const { filteredArtists } = useArtistsTable()

// Local table for display columns (different from filter columns)
import {
  useVueTable,
  getCoreRowModel,
  createColumnHelper,
} from '@tanstack/vue-table'

const columnHelper = createColumnHelper<Artist>()

const displayColumns = [
  columnHelper.accessor('profile_image_url', {
    header: () => '',
    size: 80,
    cell: props => (
      <BaseImage
        imageFile={{ url: props.row.original.profile_image_url ?? '' }}
        externalCssClass={['artist-table__profile-image']}
      />
    ),
  }),

  columnHelper.accessor('name', {
    header: () => '',
    size: 200,
    cell: info => info.getValue(),
  }),

  columnHelper.accessor('artworks', {
    header: () => '',
    size: 400,
    cell: props => (
      <div class="artist-table__artworks-preview">
        {props.row.original.artworks.map(artwork => (
          <BaseImage
            key={`${props.row.original.id}-${artwork.picture_url}`}
            imageFile={{
              url: artwork.picture_url,
              lastUpdated: artwork.year,
            }}
            externalCssClass={['artist-table__artwork-preview-image']}
          />
        ))}
      </div>
    ),
  }),
]

// Display table uses filtered data from shared composable
const displayTable = useVueTable({
  get data() {
    return filteredArtists.value
  },
  columns: displayColumns,
  getCoreRowModel: getCoreRowModel(),
})

const tableRows = computed(() => displayTable.getRowModel().rows)

/* ----------------------------
    Virtualization
----------------------------- */

const containerRef = ref<HTMLElement | null>(null)

const rowVirtualizer = useVirtualizer({
  count: () => tableRows.value.length,
  getScrollElement: () => containerRef.value,
  estimateSize: () => 90,
  overscan: 5,
})

const virtualRows = computed(() => {
  const items = rowVirtualizer.value.getVirtualItems()
  return {
    items,
    start: items.length ? items[0].start : 0,
    end:
      rowVirtualizer.value.getTotalSize() -
      (items.length ? items[items.length - 1].end : 0),
  }
})
</script>
```

**Step 2: Update template to use displayColumns**

Update the template (change `columns` to `displayColumns`):

```vue
<template>
  <div ref="containerRef" class="artists-table-wrapper">
    <table class="artists-table">
      <thead>
        <tr
          v-for="headerGroup in displayTable.getHeaderGroups()"
          :key="headerGroup.id"
        >
          <th
            v-for="header in headerGroup.headers"
            :key="header.id"
            :style="{ width: header.getSize() + 'px' }"
          >
            <FlexRender
              v-if="!header.isPlaceholder"
              :render="header.column.columnDef.header"
              :props="header.getContext()"
            />
          </th>
        </tr>
      </thead>

      <tbody>
        <!-- Spacer before -->
        <tr style="height: 0">
          <td :colspan="displayColumns.length">
            <div :style="{ height: `${virtualRows.start}px` }" />
          </td>
        </tr>

        <!-- Virtual rows -->
        <tr
          v-for="virtualRow in virtualRows.items"
          :key="tableRows[virtualRow.index].original.id"
          :style="{ transform: `translateY(${virtualRow.start}px)` }"
          @click="openModal(tableRows[virtualRow.index].original)"
        >
          <td
            v-for="cell in tableRows[virtualRow.index].getVisibleCells()"
            :key="cell.id"
            :style="{ width: cell.column.getSize() + 'px' }"
          >
            <FlexRender
              :render="cell.column.columnDef.cell"
              :props="cell.getContext()"
            />
          </td>
        </tr>

        <!-- Spacer after -->
        <tr style="height: 0">
          <td :colspan="displayColumns.length">
            <div :style="{ height: `${virtualRows.end}px` }" />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
```

**Step 3: Verify no errors**

Run: `cd frontend && yarn nuxi typecheck 2>&1 | head -50`
Expected: No errors

**Step 4: Commit**

```bash
git add frontend/components/artists-table/ArtistsTable.vue
git commit -m "refactor: ArtistsTable uses shared useArtistsTable composable"
```

---

## Task 8: Update index.vue to Use Composable for Bubble View

**Files:**
- Modify: `frontend/pages/index.vue`

**Step 1: Update script to use composable**

```vue
<script setup lang="tsx">
import { useArtistsTable } from "~/composables/useArtistsTable";
import { useArtistsStore } from "~/J/useArtistsStore";
import { randomRange } from "~/composables/useUtils";

const config = useRuntimeConfig();
const { artistsWithPositions, hasFilters, removeFilters } = useArtistsTable();
const artistsStore = useArtistsStore();
const isTable = ref(true);

type ArtistPositionUpdate = { id: string; position: { x: number; y: number } }

const handleToggleTableAndBubbles = () => {
  isTable.value = !isTable.value
}

const handleArtistPositionUpdate = ({ id, position }: ArtistPositionUpdate) => {
  artistsStore.updateArtistPosition(id, position)
}

const hasClearButton = hasFilters;

const handleClear = () => {
  removeFilters();
};

onMounted(async () => {
  const screenHeight = window.innerHeight;
  const screenWidth = window.innerWidth;
  const randomizePosition = () => {
    return {
      x: randomRange(100, screenWidth) - 139,
      y: randomRange(100, screenHeight) - 100,
    }
  };

  await artistsStore.fetchArtists(`${config.public.DJANGO_SERVER_URL}/artists/`);
  artistsStore.initializePositions(randomizePosition);
});
</script>
```

**Step 2: Update template to use artistsWithPositions**

```vue
<template>
  <div>
      <Filter />
    <div v-if="artistsStore.error" class="error-message">
      {{ artistsStore.error }}
      <button @click="() => { artistsStore.error = null; }" class="error-close">×</button>
    </div>
    <div v-if="artistsStore.isLoading" class="loading-indicator">
      Loading artists...
    </div>
    <div class="menu">
      <Sort />
      <button v-if="hasClearButton" class="clear-button" @click="handleClear" aria-label="Clear filters">
        <img src="~/assets/close.svg" width="16" :class="['filter-toggle-img']">
      </button>

      <button class="toggle-table-and-bubbles" @click="handleToggleTableAndBubbles" :aria-label="`Switch to ${isTable ? 'bubbles' : 'table'} view`">
        {{ isTable ? 'bubbles' : 'table' }}
      </button>
    </div>
    <ArtistsTable v-if="isTable"/>
    <Artist
      v-else
      v-for="artist in artistsWithPositions"
      :key="artist.id"
      :artist-data="artist"
      @update-artist-position="handleArtistPositionUpdate"
      class="artist"
      />

    <ArtistModal />
  </div>
</template>
```

**Step 3: Commit**

```bash
git add frontend/pages/index.vue
git commit -m "refactor: index.vue uses useArtistsTable for Bubble View"
```

---

## Task 9: Update Artist.vue to Use calculatedY

**Files:**
- Modify: `frontend/components/Artist.vue`

**Step 1: Update the props type and position handling**

Update the script section - change artistData type and position computed:

```vue
<script setup lang="ts">
import { useFilterStore } from '#imports'
import interact from 'interactjs'
import useArtistModal from './useArtistModal'
import useMouseActionDetector from '~/J/useMouseActionDetector'
import { type Artist } from '../J/useArtistsStore'
import type { ArtistWithPosition } from '~/composables/useArtistsTable'
import { randomRange } from '~/composables/useUtils'

const { openArtistModal } = useArtistModal()
const props = defineProps<{
  artistData: ArtistWithPosition
}>()
// ... rest of script stays the same until handlePieceStyle

const handlePieceStyle = computed(() => {
  return {
    left: `${props.artistData?.position?.x || 0}px`,
    top: `${props.artistData?.calculatedY ?? props.artistData?.position?.y ?? 0}px`,
    zIndex: `${localZIndex.value}`
  }
})
</script>
```

Note: Keep all other parts of the script the same. Only change:
1. Add import for `ArtistWithPosition`
2. Change props type from `Artist` to `ArtistWithPosition`
3. Update `handlePieceStyle` to use `calculatedY` with fallback

**Step 2: Commit**

```bash
git add frontend/components/Artist.vue
git commit -m "refactor: Artist.vue uses calculatedY from composable"
```

---

## Task 10: Update Filter.vue to Use Composable

**Files:**
- Modify: `frontend/components/Filter.vue`

**Step 1: Update script to use composable**

```vue
<script setup lang="ts">
import { useArtistsTable, type MediaTypeOptionEnum, type SelectionOptionType } from '~/composables/useArtistsTable'

const menuRef = ref<HTMLElement>()
const isOpenMenu = ref(false)

const toggleMenu = () => {
  isOpenMenu.value = !isOpenMenu.value
}

const {
  FilterOption,
  FilterType,
  mediaTypeOptions,
  genderOptions,
  selectedMediaToShow,
  selectedGendersToShow,
  searchAndFilterByName,
  filterByGender,
  filterByMediaType,
  filterByBornInRange,
} = useArtistsTable()

const handleMediaTypeSelection = (selectionOption?: SelectionOptionType<any>) => {
  if (!selectionOption) {
    return
  }
  filterByMediaType(selectionOption as SelectionOptionType<MediaTypeOptionEnum>)
}

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as Node | null
  if (menuRef.value && target && !menuRef.value.contains(target)) {
    isOpenMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
```

**Step 2: Update template to use composable values**

```vue
<template>
  <div class="filter" ref="menuRef">
      <FilterOption
        :filterOption="FilterOption.NAME"
        label=""
        @search="searchAndFilterByName"
        :filterType="FilterType.SEARCH"
      />
    <button
      :class="['filter-toggle']"
      @click="toggleMenu"
      :aria-expanded="isOpenMenu"
      aria-controls="filter-menu"
      aria-label="Toggle filter menu"
      type="button"
    >
      filter
    </button>

    <div v-if="isOpenMenu" id="filter-menu" class="filter__menu" role="menu">
      <FilterOption
        :filterOption="FilterOption.MEDIA_TYPE"
        :selectionOptions="mediaTypeOptions"
        :selectedOptions="selectedMediaToShow"
        @selection="handleMediaTypeSelection"
        :filterType="FilterType.SELECTION_TEXT"
      />
      <FilterOption
        :filterOption="FilterOption.GENDER"
        :selectionOptions="genderOptions"
        :selectedOptions="selectedGendersToShow"
        @selection="filterByGender"
        :filterType="FilterType.SELECTION"
      />
      <FilterOption
        :filterOption="FilterOption.BORN"
        label="born"
        @range="filterByBornInRange"
        :filterType="FilterType.RANGE"
      />
    </div>
  </div>
</template>
```

**Step 3: Commit**

```bash
git add frontend/components/Filter.vue
git commit -m "refactor: Filter.vue uses useArtistsTable composable"
```

---

## Task 11: Update filter/Option.vue to Use Composable

**Files:**
- Modify: `frontend/components/filter/Option.vue`

**Step 1: Update script to use composable**

```vue
<script setup lang="ts">
import { useArtistsTable, FilterType, type FilterOption, type SelectionOptionType } from '~/composables/useArtistsTable'

const { textToSearch, rangeFrom, rangeTo } = useArtistsTable()

const props = defineProps<{
  filterOption: FilterOption
  label?: string
  filterType: FilterType
  selectionOptions?: SelectionOptionType<any>[]
  selectedOptions?: SelectionOptionType<any>[]
}>()

const emit = defineEmits<{
  (e: 'search', text: string): void
  (e: 'range', rangeFrom: number | null, rangeTo: number | null): void
  (e: 'selection', selectedOption?: SelectionOptionType<any>): void
}>()

// Convert string refs to number refs for v-model.number
const rangeFromNumber = computed({
  get: () => {
    const val = rangeFrom.value
    if (val === '') return null
    const parsed = Number(val)
    return Number.isNaN(parsed) ? null : parsed
  },
  set: (val: number | null) => {
    rangeFrom.value = val === null || isNaN(val) ? '' : String(val)
  }
})

const rangeToNumber = computed({
  get: () => {
    const val = rangeTo.value
    if (val === '') return null
    const parsed = Number(val)
    return Number.isNaN(parsed) ? null : parsed
  },
  set: (val: number | null) => {
    rangeTo.value = val === null || isNaN(val) ? '' : String(val)
  }
})

const handleSearchInputChange = () => {
  emit('search', textToSearch.value)
}

const handleRangeChange = () => {
  emit('range', rangeFromNumber.value, rangeToNumber.value)
}

const handleSelectionChange = (selectionOption: SelectionOptionType<any>) => {
  emit('selection', selectionOption)
}

const isOptionSelected = (selectionOption: SelectionOptionType<any>) => {
  return props.selectedOptions?.some((selectedOption) => selectedOption.enumValue === selectionOption.enumValue)
}
</script>
```

**Step 2: Commit**

```bash
git add frontend/components/filter/Option.vue
git commit -m "refactor: filter/Option.vue uses useArtistsTable composable"
```

---

## Task 12: Update Sort.vue to Use Composable

**Files:**
- Modify: `frontend/components/Sort.vue`

**Step 1: Update script to use composable**

```vue
<script setup lang="ts">
import { useArtistsTable } from '~/composables/useArtistsTable'

const menuRef = ref<HTMLElement>()
const isOpenMenu = ref(false)

const toggleMenu = () => {
  isOpenMenu.value = !isOpenMenu.value
}

const { SortOption } = useArtistsTable()

const handleClickOutside = (event: MouseEvent | TouchEvent) => {
  if (menuRef.value && !menuRef.value.contains(event.target as Node)) {
    isOpenMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
```

**Step 2: Update template**

```vue
<template>
  <div class="sort" ref="menuRef">
    <button
      class="sort__toggle"
      @click="toggleMenu"
      :aria-expanded="isOpenMenu"
      aria-controls="sort-menu"
      aria-label="Toggle sort menu"
      type="button"
    >
      <img src="~/assets/sort.svg" width="30" alt="Sort">
    </button>
    <div v-if="isOpenMenu" id="sort-menu" class="sort__menu" role="menu">
      <SortOption :sortOption="SortOption.SURNAME" label="name" class="name-sort" isSortSignBeforeText/>
      <SortOption :sortOption="SortOption.BORN" label="born" class="born-sort" isSortSignBeforeText/>
      <SortOption :sortOption="SortOption.AUCTIONS_TURNOVER_2023_H1_USD" label="auctions 2023" class="auctions-sort" :isSortSignBeforeText="false"/>
    </div>
  </div>
</template>
```

**Step 3: Commit**

```bash
git add frontend/components/Sort.vue
git commit -m "refactor: Sort.vue uses useArtistsTable composable"
```

---

## Task 13: Update sort/Option.vue to Use Composable

**Files:**
- Modify: `frontend/components/sort/Option.vue`

**Step 1: Update script to use composable**

```vue
<script setup lang="ts">
import { useArtistsTable, type SortOption, SortDirection } from '~/composables/useArtistsTable'

const props = defineProps<{
  sortOption: SortOption
  label?: string
  isSortSignBeforeText?: boolean
}>()

const { setSort, activeSort } = useArtistsTable()
</script>
```

**Step 2: Update template**

```vue
<template>
  <div class="sort-option" @click="setSort(sortOption)">
        <span v-if="activeSort.field === sortOption && isSortSignBeforeText">
          <span v-if="activeSort.direction === SortDirection.ASC">
            △
          </span>
          <span v-else> ▼ </span>
        </span>
        {{ label || sortOption }}
        <span v-if="activeSort.field === sortOption && !isSortSignBeforeText">
          <span v-if="activeSort.direction === SortDirection.ASC">
            △
          </span>
          <span v-else> ▼ </span>
        </span>
      </div>
</template>
```

**Step 3: Commit**

```bash
git add frontend/components/sort/Option.vue
git commit -m "refactor: sort/Option.vue uses useArtistsTable composable"
```

---

## Task 14: Update useArtistsStore - Remove Redundant State

**Files:**
- Modify: `frontend/J/useArtistsStore.ts`

**Step 1: Remove the `artists` ref and related methods**

Update the store to only keep `artistsAll`:

```typescript
export type Artist = {
  id: string
  profile_image_url: string
  name: string
  surname: string
  firstname: string
  notes: string
  born: number
  artworks: {
    id?: number
    picture_url: string
    title: string
    year: number
    sizeY: number
    sizeX: number
  }[]
  position: {
    x: number
    y: number
  }
  gender: "W" | "M" | "N"
  auctions_turnover_2023_h1_USD: number
  similar_authors_postgres_ids: string[]
  media_types: ('nft' | 'digital' | 'painting' | 'sculpture')[]
}

export const useArtistsStore = defineStore('artists', () => {
  const artistsAll = ref<Artist[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const fetchArtists = async (apiUrl: string) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await $fetch<{ success: boolean; data?: Artist[]; error?: string }>(apiUrl)

      if (!response?.success) {
        error.value = response?.error || 'Failed to load artists'
        console.error("Error: failed to load artists", response?.error)
        return
      }

      const fetchedArtists = response.data ?? []
      artistsAll.value = fetchedArtists
    } catch (err: unknown) {
      if (err instanceof Error && (err.name === 'AbortError' || (err as any).code === 'ECONNABORTED')) {
        error.value = "Request timed out. Please try again."
      } else if (err && typeof err === 'object' && ('status' in err || 'statusCode' in err)) {
        const status = (err as { status?: number; statusCode?: number }).status || (err as { status?: number; statusCode?: number }).statusCode
        const errData = (err as { data?: unknown }).data
        const dataMessage = errData ? `: ${typeof errData === 'string' ? errData : JSON.stringify(errData)}` : ''
        error.value = `Server error: ${status}${dataMessage}`
      } else if (err instanceof Error) {
        error.value = err.message
      } else {
        error.value = "An unknown error occurred. Please try again."
      }
      console.error("Error fetching artists:", err)
    } finally {
      isLoading.value = false
    }
  }

  const updateArtistPosition = (id: string, position: { x: number; y: number }) => {
    const artist = artistsAll.value.find((item) => item.id === id)
    if (artist) {
      artist.position = { ...position }
    }
  }

  const initializePositions = (randomizePositionFn: () => { x: number; y: number }) => {
    artistsAll.value.forEach((artist) => {
      artist.position = randomizePositionFn()
    })
  }

  return {
    // State
    artistsAll,
    isLoading,
    error,
    // Actions
    fetchArtists,
    updateArtistPosition,
    initializePositions,
  }
})
```

**Step 2: Commit**

```bash
git add frontend/J/useArtistsStore.ts
git commit -m "refactor: simplify useArtistsStore - remove redundant artists ref"
```

---

## Task 15: Delete Old Store Files

**Files:**
- Delete: `frontend/J/useFilterStore.ts`
- Delete: `frontend/J/useSortStore.ts`
- Delete: `frontend/composables/useArtistArrangement.ts`

**Step 1: Remove the files**

```bash
rm frontend/J/useFilterStore.ts
rm frontend/J/useSortStore.ts
rm frontend/composables/useArtistArrangement.ts
```

**Step 2: Verify removal**

Run: `ls frontend/J/`
Expected: Only `useArtistsStore.ts` and `useMouseActionDetector.ts`

**Step 3: Commit**

```bash
git add -A
git commit -m "chore: remove old filter/sort stores and arrangement composable"
```

---

## Task 16: Fix Any Remaining Import Errors

**Files:**
- Check all files for broken imports

**Step 1: Search for old imports**

```bash
cd frontend && grep -r "useFilterStore\|useSortStore\|useArtistArrangement" --include="*.vue" --include="*.ts" .
```

Expected: No results (all migrated)

**Step 2: Run type check**

```bash
cd frontend && yarn nuxi typecheck
```

Expected: No errors

**Step 3: If errors found, fix them**

Common fixes:
- Update imports to use `useArtistsTable`
- Remove unused imports

**Step 4: Commit any fixes**

```bash
git add -A
git commit -m "fix: resolve remaining import errors after migration"
```

---

## Task 17: Manual Testing

**Step 1: Start the development server**

```bash
cd frontend && yarn dev
```

**Step 2: Test filtering**

- [ ] Text search filters artists by name
- [ ] Born range filter (min only, max only, both)
- [ ] Gender filter (single, multiple)
- [ ] Media type filter (single, multiple)
- [ ] Clear filters button works

**Step 3: Test sorting**

- [ ] Sort by name (ASC/DESC toggle)
- [ ] Sort by born year (ASC/DESC toggle)
- [ ] Sort by auctions (ASC/DESC toggle)

**Step 4: Test both views**

- [ ] Table View shows filtered/sorted data
- [ ] Bubble View shows filtered/sorted data with correct positions
- [ ] Toggle between views preserves filter state

**Step 5: Test interactions**

- [ ] Dragging artists in Bubble View works
- [ ] Clicking artist opens modal
- [ ] Virtualization in Table View works (scroll performance)

---

## Task 18: Final Commit

**Step 1: If all tests pass, create final commit**

```bash
git add -A
git commit -m "feat: complete TanStack unified filtering/sorting migration

- Created useArtistsTable composable as single source of truth
- Migrated all filtering logic to TanStack column filters
- Migrated all sorting logic to TanStack sorting
- Position calculation now derived from sort order
- Removed useFilterStore, useSortStore, useArtistArrangement
- Updated all components to use new composable"
```

---

## Rollback Instructions

If something goes wrong:

```bash
# Reset to before migration
git log --oneline -20  # Find commit before migration started
git reset --hard <commit-hash>
```
