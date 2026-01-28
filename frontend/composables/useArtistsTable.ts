import { ref, computed, watch, h } from 'vue'
import {
  useVueTable,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  createColumnHelper,
  type ColumnFiltersState,
  type SortingState,
  type VisibilityState,
  type Table,
  type FilterFn,
} from '@tanstack/vue-table'
import { useArtistsStore, type Artist } from '~/J/useArtistsStore'
import { useArtistArrangement } from '~/composables/useArtistArrangement'
import BaseImage from '~/components/BaseImage.vue'
import {
  type BornRangeFilter,
  isBornInRange,
  matchesIdFilter,
  matchesGenderFilter,
  matchesMediaTypeFilter,
  toggleSort,
} from '~/composables/artistsTableUtils'
import {
  FilterOption,
  FilterType,
  GenderOptionEnum,
  MediaTypeOptionEnum,
  type SelectionOptionType,
} from '~/J/useFilterStore'
import {
  SortOption,
  SortDirection,
} from '~/J/useSortStore'

// Re-export for backward compatibility
// export { GenderOptionEnum, MediaTypeOptionEnum, FilterOption, FilterType, SortOption, SortDirection }
// export type { SelectionOptionType }

// Icons
import FluidSvg from '~/assets/fluid.svg'
import FemalePng from '~/assets/female.png'
import MalePng from '~/assets/male.png'

export type ArtistWithPosition = Artist & {
  calculatedY: number
}

// ============================================================================
// Options for UI
// ============================================================================

export const genderOptions: SelectionOptionType<GenderOptionEnum>[] = [
  { sign: FluidSvg, enumValue: GenderOptionEnum.NON_BINARY },
  { sign: MalePng, enumValue: GenderOptionEnum.MAN },
  { sign: FemalePng, enumValue: GenderOptionEnum.WOMAN },
]

export const mediaTypeOptions: SelectionOptionType<MediaTypeOptionEnum>[] = [
  { text: 'painting', enumValue: MediaTypeOptionEnum.PAINTING },
  { text: 'nft', enumValue: MediaTypeOptionEnum.NFT },
  { text: 'sculpture', enumValue: MediaTypeOptionEnum.SCULPTURE },
]

// ============================================================================
// Shared State (singleton across components)
// ============================================================================

const columnFilters = ref<ColumnFiltersState>([])
const globalFilter = ref('')
const sorting = ref<SortingState>([])
const columnVisibility = ref<VisibilityState>({
  id: false,
  profile_image_url: true,
  name: true,
  artworks: true,
  firstname: false,
  surname: false,
  born: false,
  gender: false,
  media_types: false,
  auctions_turnover_2023_h1_USD: false,
})

const rangeFrom = ref<string>('')
const rangeTo = ref<string>('')
const selectedGendersToShow = ref<SelectionOptionType<GenderOptionEnum>[]>([])
const selectedMediaToShow = ref<SelectionOptionType<MediaTypeOptionEnum>[]>([])
const textToSearch = ref<string>('')
const isFilteringInProgress = ref(false)
const filteredIds = ref<string[]>([])

let tableInstance: Table<Artist> | null = null

// ============================================================================
// Custom Filter Functions
// ============================================================================

/**
 * Filter by birth year range (from/to)
 */
const bornRangeFilter: FilterFn<Artist> = (row, columnId, filterValue: BornRangeFilter) => {
  const born = row.getValue<number>(columnId)
  return isBornInRange(born, filterValue)
}

/**
 * Filter by gender enums (maps N->NON_BINARY, W->WOMAN, M->MAN)
 */
const genderFilter: FilterFn<Artist> = (row, columnId, filterValue: GenderOptionEnum[]) => {
  const gender = row.getValue<'N' | 'W' | 'M'>(columnId)
  return matchesGenderFilter(gender, filterValue)
}

/**
 * Filter by media type enums (lowercase comparison)
 */
const mediaTypeFilter: FilterFn<Artist> = (
  row,
  columnId,
  filterValue: MediaTypeOptionEnum[]
) => {
  const mediaTypes = row.getValue<('nft' | 'digital' | 'painting' | 'sculpture')[]>(columnId)
  return matchesMediaTypeFilter(mediaTypes, filterValue)
}

/**
 * Filter by ID list (used for AI image search results)
 */
const idListFilter: FilterFn<Artist> = (row, columnId, filterValue: string[]) => {
  const id = row.getValue<string>(columnId)
  return matchesIdFilter(String(id), filterValue)
}

// ============================================================================
// Position Calculation
// ============================================================================

const INITIAL_Y = 200
const SPACING = 120

/**
 * Calculate Y positions for artists based on sort field grouping
 * Groups artists with the same sort field value at the same Y position
 * Spaces different groups 120px apart
 */
const calculatePositions = (
  artists: Artist[],
  sortField: string | null
): ArtistWithPosition[] => {
  if (artists.length === 0) return []

  let currentY = INITIAL_Y

  return artists.map((artist, index) => {
    if (index === 0) {
      return { ...artist, calculatedY: currentY }
    }

    const previousArtist = artists[index - 1]

    // If no sort field, each artist gets its own row
    if (!sortField) {
      currentY += SPACING
      return { ...artist, calculatedY: currentY }
    }

    // Check if current artist has the same field value as previous
    const currentValue = (artist as Record<string, unknown>)[sortField]
    const previousValue = (previousArtist as Record<string, unknown>)[sortField]
    const hasSameValue = currentValue === previousValue

    if (!hasSameValue) {
      currentY += SPACING
    }

    return { ...artist, calculatedY: currentY }
  })
}

// ============================================================================
// Column Helper & Definitions
// ============================================================================

const columnHelper = createColumnHelper<Artist>()

const columns = [
  columnHelper.accessor('id', {
    header: 'ID',
    cell: (info) => info.getValue(),
    filterFn: idListFilter,
    size: 60,
  }),
  columnHelper.accessor('profile_image_url', {
    header: () => '',
    cell: (props) =>
      h(BaseImage, {
        imageFile: { url: props.row.original.profile_image_url ?? '' },
        externalCssClass: ['artist-table__profile-image'],
        key: props.row.original.id,
      }),
    enableSorting: false,
    size: 50,
  }),
  columnHelper.accessor('name', {
    header: () => '',
    cell: (info) => info.getValue(),
    enableGlobalFilter: true,
    size: 150,
  }),
  columnHelper.accessor('artworks', {
    header: () => '',
    cell: (props) =>
      h(
        'div',
        { class: 'artist-table__artworks-preview', key: `${props.row.original.id}-artworks` },
        props.row.original.artworks.map((artwork) =>
          h(BaseImage, {
            key: `${props.row.original.id}-artwork-${artwork.id ?? artwork.title}`,
            imageFile: {
              url: artwork.picture_url,
              lastUpdated: artwork.year,
            },
            externalCssClass: ['artist-table__artwork-preview-image'],
          })
        )
      ),
    enableSorting: false,
    size: 250,
  }),
  columnHelper.accessor('firstname', {
    header: 'First Name',
    cell: (info) => info.getValue(),
    enableGlobalFilter: true,
    enableSorting: true,
  }),
  columnHelper.accessor('surname', {
    header: 'Surname',
    cell: (info) => info.getValue(),
    enableGlobalFilter: true,
    enableSorting: true,
  }),
  columnHelper.accessor('born', {
    header: 'Born',
    cell: (info) => info.getValue(),
    filterFn: bornRangeFilter,
    enableSorting: true,
  }),
  columnHelper.accessor('gender', {
    header: 'Gender',
    cell: (info) => info.getValue(),
    filterFn: genderFilter,
    enableSorting: true,
  }),
  columnHelper.accessor('media_types', {
    header: 'Media Types',
    cell: (info) => info.getValue()?.join(', ') ?? '',
    filterFn: mediaTypeFilter,
  }),
  columnHelper.accessor('auctions_turnover_2023_h1_USD', {
    header: 'Auction Turnover (2023 H1)',
    cell: (info) => {
      const value = info.getValue()
      return value ? `$${value.toLocaleString()}` : '-'
    },
    enableSorting: true,
  }),
]

// ============================================================================
// Main Composable
// ============================================================================

export const useArtistsTable = () => {
  const artistsStore = useArtistsStore()
  const { reArrangeSortedArtists } = useArtistArrangement()

  // -------------------------------------------------------------------------
  // State: TanStack Table
  // -------------------------------------------------------------------------
  // (shared state defined above to keep a single instance across components)

  // -------------------------------------------------------------------------
  // TanStack Table Instance
  // -------------------------------------------------------------------------
  if (!tableInstance) {
    tableInstance = useVueTable<Artist>({
      get data() {
        return artistsStore.artistsAll
      },
      columns,
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
      get columnVisibility() {
        return columnVisibility.value
      },
      },
      onColumnFiltersChange: (updaterOrValue) => {
        columnFilters.value =
          typeof updaterOrValue === 'function'
            ? updaterOrValue(columnFilters.value)
            : updaterOrValue
      },
      onGlobalFilterChange: (updaterOrValue) => {
        globalFilter.value =
          typeof updaterOrValue === 'function'
            ? updaterOrValue(globalFilter.value)
            : updaterOrValue
      },
      onSortingChange: (updaterOrValue) => {
        sorting.value =
          typeof updaterOrValue === 'function'
            ? updaterOrValue(sorting.value)
            : updaterOrValue
      },
    onColumnVisibilityChange: (updaterOrValue) => {
      columnVisibility.value =
        typeof updaterOrValue === 'function'
          ? updaterOrValue(columnVisibility.value)
          : updaterOrValue
    },
      getCoreRowModel: getCoreRowModel(),
      getFilteredRowModel: getFilteredRowModel(),
      getSortedRowModel: getSortedRowModel(),
      globalFilterFn: 'includesString',
    })
  }

  const table = tableInstance as Table<Artist>

  // -------------------------------------------------------------------------
  // Computed: Derived Data
  // -------------------------------------------------------------------------

  /**
   * Get the filtered and sorted artists from the table
   */
  const filteredArtists = computed<Artist[]>(() => {
    return table.getRowModel().rows.map((row) => row.original)
  })

  /**
   * Get the current active sort field and direction
   */
  const activeSort = computed<{
    field: SortOption | null
    direction: SortDirection | null
  }>(() => {
    if (sorting.value.length === 0) {
      return { field: null, direction: null }
    }

    const sort = sorting.value[0]
    if (!sort) {
      return { field: null, direction: null }
    }
    const direction = sort.desc ? SortDirection.DESC : SortDirection.ASC

    // Map column ID to SortOption enum
    let field: SortOption | null = null
    switch (sort.id) {
      case 'firstname':
        field = SortOption.FIRSTNAME
        break
      case 'surname':
        field = SortOption.SURNAME
        break
      case 'born':
        field = SortOption.BORN
        break
      case 'gender':
        field = SortOption.GENDER
        break
      case 'auctions_turnover_2023_h1_USD':
        field = SortOption.AUCTIONS_TURNOVER_2023_H1_USD
        break
    }

    return { field, direction }
  })

  /**
   * Check if any filters are active
   */
  const hasFilters = computed<boolean>(() => {
    return (
      !!rangeFrom.value ||
      !!rangeTo.value ||
      !!textToSearch.value ||
      filteredIds.value.length > 0 ||
      selectedGendersToShow.value.length > 0 ||
      selectedMediaToShow.value.length > 0
    )
  })

  /**
   * Get artists with calculated Y positions for bubble view
   */
  const artistsWithPositions = computed<ArtistWithPosition[]>(() => {
    const sortField = sorting.value[0]?.id ?? null
    return calculatePositions(filteredArtists.value, sortField)
  })

  const arrangeBubblePositions = () => {
    const sortField = sorting.value[0]?.id
    const fallbackField: 'firstname' = 'firstname'

    if (
      sortField === 'firstname' ||
      sortField === 'surname' ||
      sortField === 'born' ||
      sortField === 'gender' ||
      sortField === 'auctions_turnover_2023_h1_USD'
    ) {
      reArrangeSortedArtists(sortField)
      return
    }

    reArrangeSortedArtists(fallbackField)
  }

  watch(
    [filteredArtists, sorting],
    ([nextArtists]) => {
      // Preserve positions from artistsAll when setting filtered artists
      const artistsWithPositions = nextArtists.map((artist) => {
        const originalArtist = artistsStore.artistsAll.find((a) => a.id === artist.id)
        return {
          ...artist,
          position: originalArtist?.position ?? artist.position ?? { x: 0, y: 0 },
        }
      })
      artistsStore.setArtists(artistsWithPositions)
      arrangeBubblePositions()
    },
    { immediate: true }
  )

  // -------------------------------------------------------------------------
  // Methods: Filtering
  // -------------------------------------------------------------------------

  /**
   * Search and filter by name (uses global filter)
   */
  const searchAndFilterByName = (whatToSearch: string) => {
    textToSearch.value = whatToSearch
    globalFilter.value = whatToSearch
  }

  /**
   * Filter by birth year range
   */
  const filterByBornInRange = (from: number | null, to: number | null) => {
    const hasFrom = from !== null && !isNaN(from)
    const hasTo = to !== null && !isNaN(to)

    rangeFrom.value = hasFrom ? String(from) : ''
    rangeTo.value = hasTo ? String(to) : ''

    if (!hasFrom && !hasTo) {
      // Remove the born filter
      columnFilters.value = columnFilters.value.filter((f) => f.id !== 'born')
    } else {
      // Update or add the born filter
      const existingIndex = columnFilters.value.findIndex((f) => f.id === 'born')
      const newFilter = {
        id: 'born',
        value: {
          from: hasFrom ? from : null,
          to: hasTo ? to : null,
        },
      }

      if (existingIndex >= 0) {
        columnFilters.value = [
          ...columnFilters.value.slice(0, existingIndex),
          newFilter,
          ...columnFilters.value.slice(existingIndex + 1),
        ]
      } else {
        columnFilters.value = [...columnFilters.value, newFilter]
      }
    }
  }

  /**
   * Toggle a gender filter option
   */
  const filterByGender = (selectedGender?: SelectionOptionType<GenderOptionEnum>) => {
    if (!selectedGender) return

    const isAlreadySelected = selectedGendersToShow.value.some(
      (option) => option.enumValue === selectedGender.enumValue
    )

    if (isAlreadySelected) {
      selectedGendersToShow.value = selectedGendersToShow.value.filter(
        (o) => o.enumValue !== selectedGender.enumValue
      )
    } else {
      selectedGendersToShow.value = [...selectedGendersToShow.value, selectedGender]
    }

    // Update column filter
    if (selectedGendersToShow.value.length === 0) {
      columnFilters.value = columnFilters.value.filter((f) => f.id !== 'gender')
    } else {
      const genderEnums = selectedGendersToShow.value.map((o) => o.enumValue)
      const existingIndex = columnFilters.value.findIndex((f) => f.id === 'gender')
      const newFilter = { id: 'gender', value: genderEnums }

      if (existingIndex >= 0) {
        columnFilters.value = [
          ...columnFilters.value.slice(0, existingIndex),
          newFilter,
          ...columnFilters.value.slice(existingIndex + 1),
        ]
      } else {
        columnFilters.value = [...columnFilters.value, newFilter]
      }
    }
  }

  /**
   * Toggle a media type filter option
   */
  const filterByMediaType = (selectedMediaType?: SelectionOptionType<MediaTypeOptionEnum>) => {
    if (!selectedMediaType) return

    const isAlreadySelected = selectedMediaToShow.value.some(
      (option) => option.enumValue === selectedMediaType.enumValue
    )

    if (isAlreadySelected) {
      selectedMediaToShow.value = selectedMediaToShow.value.filter(
        (o) => o.enumValue !== selectedMediaType.enumValue
      )
    } else {
      selectedMediaToShow.value = [...selectedMediaToShow.value, selectedMediaType]
    }

    // Update column filter
    if (selectedMediaToShow.value.length === 0) {
      columnFilters.value = columnFilters.value.filter((f) => f.id !== 'media_types')
    } else {
      const mediaEnums = selectedMediaToShow.value.map((o) => o.enumValue)
      const existingIndex = columnFilters.value.findIndex((f) => f.id === 'media_types')
      const newFilter = { id: 'media_types', value: mediaEnums }

      if (existingIndex >= 0) {
        columnFilters.value = [
          ...columnFilters.value.slice(0, existingIndex),
          newFilter,
          ...columnFilters.value.slice(existingIndex + 1),
        ]
      } else {
        columnFilters.value = [...columnFilters.value, newFilter]
      }
    }
  }

  /**
   * Filter by a list of artist IDs
   */
  const filterByIds = (ids: (string | number)[]) => {
    filteredIds.value = ids.map((id) => String(id))

    if (filteredIds.value.length === 0) {
      columnFilters.value = columnFilters.value.filter((f) => f.id !== 'id')
      return
    }

    const existingIndex = columnFilters.value.findIndex((f) => f.id === 'id')
    const newFilter = { id: 'id', value: filteredIds.value }

    if (existingIndex >= 0) {
      columnFilters.value = [
        ...columnFilters.value.slice(0, existingIndex),
        newFilter,
        ...columnFilters.value.slice(existingIndex + 1),
      ]
    } else {
      columnFilters.value = [...columnFilters.value, newFilter]
    }
  }

  /**
   * Remove all filters
   */
  const removeFilters = () => {
    selectedGendersToShow.value = []
    selectedMediaToShow.value = []
    textToSearch.value = ''
    rangeFrom.value = ''
    rangeTo.value = ''
    filteredIds.value = []
    globalFilter.value = ''
    columnFilters.value = []
  }

  // -------------------------------------------------------------------------
  // Methods: Sorting
  // -------------------------------------------------------------------------

  /**
   * Set or toggle sort on a field
   * Toggles between ASC and DESC, defaults to ASC for new fields
   */
  const setSort = (field: SortOption) => {
    // Map SortOption to column ID
    let columnId: string
    switch (field) {
      case SortOption.FIRSTNAME:
        columnId = 'firstname'
        break
      case SortOption.SURNAME:
        columnId = 'surname'
        break
      case SortOption.BORN:
        columnId = 'born'
        break
      case SortOption.GENDER:
        columnId = 'gender'
        break
      case SortOption.AUCTIONS_TURNOVER_2023_H1_USD:
        columnId = 'auctions_turnover_2023_h1_USD'
        break
    }

    sorting.value = toggleSort(sorting.value, columnId)
  }

  // -------------------------------------------------------------------------
  // Return Public API
  // -------------------------------------------------------------------------
  return {
    // TanStack Table instance
    table,

    // State
    columnFilters,
    globalFilter,
    sorting,
    rangeFrom,
    rangeTo,
    selectedGendersToShow,
    selectedMediaToShow,
    textToSearch,
    filteredIds,
    isFilteringInProgress,

    // Computed
    filteredArtists,
    artistsWithPositions,
    activeSort,
    hasFilters,

    // Filter methods
    searchAndFilterByName,
    filterByBornInRange,
    filterByGender,
    filterByMediaType,
    filterByIds,
    removeFilters,

    // Sort methods
    setSort,

    // Options for UI
    genderOptions,
    mediaTypeOptions,

    // Enums (re-exported for convenience)
    FilterOption,
    FilterType,
    SortOption,
    SortDirection,
    GenderOptionEnum,
    MediaTypeOptionEnum,
  }
}
