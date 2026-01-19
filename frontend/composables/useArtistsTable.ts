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

// Icons
import FluidSvg from '~/assets/fluid.svg'
import FemalePng from '~/assets/female.png'
import MalePng from '~/assets/male.png'

// ============================================================================
// Enums
// ============================================================================

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

// ============================================================================
// Types
// ============================================================================

export type SelectionOptionType<T> = {
  text?: string
  sign?: string
  enumValue: T
}

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
// Custom Filter Functions
// ============================================================================

/**
 * Filter by birth year range (from/to)
 */
const bornRangeFilter: FilterFn<Artist> = (
  row,
  columnId,
  filterValue: { from: number | null; to: number | null }
) => {
  const born = row.getValue<number>(columnId)
  const { from, to } = filterValue

  if (from !== null && to !== null) {
    return born >= from && born <= to
  }
  if (from !== null) {
    return born >= from
  }
  if (to !== null) {
    return born <= to
  }
  return true
}

/**
 * Filter by gender enums (maps N->NON_BINARY, W->WOMAN, M->MAN)
 */
const genderFilter: FilterFn<Artist> = (
  row,
  columnId,
  filterValue: GenderOptionEnum[]
) => {
  if (!filterValue || filterValue.length === 0) return true

  const gender = row.getValue<'N' | 'W' | 'M'>(columnId)

  return filterValue.some((option) => {
    if (option === GenderOptionEnum.NON_BINARY && gender === 'N') return true
    if (option === GenderOptionEnum.WOMAN && gender === 'W') return true
    if (option === GenderOptionEnum.MAN && gender === 'M') return true
    return false
  })
}

/**
 * Filter by media type enums (lowercase comparison)
 */
const mediaTypeFilter: FilterFn<Artist> = (
  row,
  columnId,
  filterValue: MediaTypeOptionEnum[]
) => {
  if (!filterValue || filterValue.length === 0) return true

  const mediaTypes = row.getValue<('nft' | 'digital' | 'painting' | 'sculpture')[]>(columnId)

  return filterValue.some((option) => {
    const mediaTypeLower = option.toLowerCase() as 'nft' | 'digital' | 'painting' | 'sculpture'
    return mediaTypes.includes(mediaTypeLower)
  })
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
  columnHelper.accessor('name', {
    header: 'Name',
    cell: (info) => info.getValue(),
    enableGlobalFilter: true,
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
  columnHelper.accessor('profile_image_url', {
    header: 'Profile Image',
    cell: (info) => info.getValue(),
    enableSorting: false,
  }),
  columnHelper.accessor('artworks', {
    header: 'Artworks',
    cell: (info) => info.getValue()?.length ?? 0,
    enableSorting: false,
  }),
]

// ============================================================================
// Main Composable
// ============================================================================

export const useArtistsTable = () => {
  const artistsStore = useArtistsStore()

  // -------------------------------------------------------------------------
  // State: TanStack Table
  // -------------------------------------------------------------------------
  const columnFilters = ref<ColumnFiltersState>([])
  const globalFilter = ref('')
  const sorting = ref<SortingState>([])

  // -------------------------------------------------------------------------
  // State: UI Filter Controls
  // -------------------------------------------------------------------------
  const rangeFrom = ref<string>('')
  const rangeTo = ref<string>('')
  const selectedGendersToShow = ref<SelectionOptionType<GenderOptionEnum>[]>([])
  const selectedMediaToShow = ref<SelectionOptionType<MediaTypeOptionEnum>[]>([])
  const textToSearch = ref<string>('')
  const isFilteringInProgress = ref(false)

  // -------------------------------------------------------------------------
  // TanStack Table Instance
  // -------------------------------------------------------------------------
  const table = useVueTable({
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
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    globalFilterFn: 'includesString',
  })

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
      selectedGendersToShow.value.length > 0 ||
      selectedMediaToShow.value.length > 0
    )
  })

  /**
   * Get artists with calculated Y positions for bubble view
   */
  const artistsWithPositions = computed<ArtistWithPosition[]>(() => {
    const sortField = sorting.value.length > 0 ? sorting.value[0].id : null
    return calculatePositions(filteredArtists.value, sortField)
  })

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
   * Remove all filters
   */
  const removeFilters = () => {
    selectedGendersToShow.value = []
    selectedMediaToShow.value = []
    textToSearch.value = ''
    rangeFrom.value = ''
    rangeTo.value = ''
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

    const currentSort = sorting.value.find((s) => s.id === columnId)

    if (currentSort) {
      // Toggle direction
      sorting.value = [{ id: columnId, desc: !currentSort.desc }]
    } else {
      // New sort, start with ASC (desc: false)
      sorting.value = [{ id: columnId, desc: false }]
    }
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
