import { useArtistsStore } from './useArtistsStore'
import { sleep } from '~/J/useUtils'
import { useArtistArrangement } from '~/J/useArtistArrangement'

export enum SortOption {
  'FIRSTNAME',
  'SURNAME',
  'BORN',
  'GENDER',
  'AUCTIONS_TURNOVER_2023_H1_USD'
}

export enum SortDirection {
  'ASC',
  'DESC',
  'ARRAY_WITH_ORDER'
}

export const useSortStore = defineStore('sort', () => {
  const { reArrangeSortedArtists } = useArtistArrangement()

  const activeSort = ref<{
    field: SortOption | null
    direction: SortDirection | null
  }>({
    field: null,
    direction: null
  })

  const isSortingInProgress = ref(false)

  const alphabetSort = async (fieldName: 'firstname' | 'surname' | 'gender') => {
    isSortingInProgress.value = true

    try {
      const artistsStore = useArtistsStore()
      const sortedArtists = [...artistsStore.artists]

      if (activeSort.value.direction === SortDirection.ASC) {
        sortedArtists.sort((a, b) => {
          const aValue = String(a[fieldName] ?? '')
          const bValue = String(b[fieldName] ?? '')
          return aValue.localeCompare(bValue)
        })
      } else {
        sortedArtists.sort((a, b) => {
          const aValue = String(a[fieldName] ?? '')
          const bValue = String(b[fieldName] ?? '')
          return bValue.localeCompare(aValue)
        })
      }

      artistsStore.setArtists(sortedArtists)
      await sleep(100)
      reArrangeSortedArtists(fieldName)
    } finally {
      setTimeout(() => {
        isSortingInProgress.value = false
      }, 1000)
    }
  }

  const numberSort = async (fieldName: 'born' | 'auctions_turnover_2023_h1_USD') => {
    isSortingInProgress.value = true

    try {
      const artistsStore = useArtistsStore()
      const sortedArtists = [...artistsStore.artists]

      if (activeSort.value.direction === SortDirection.ASC) {
        sortedArtists.sort((a, b) => {
          const aValue = a[fieldName] ?? null
          const bValue = b[fieldName] ?? null
          // Handle nulls: null values go to the end
          if (aValue === null && bValue === null) return 0
          if (aValue === null) return 1
          if (bValue === null) return -1
          return bValue - aValue
        })
      } else {
        sortedArtists.sort((a, b) => {
          const aValue = a[fieldName] ?? null
          const bValue = b[fieldName] ?? null
          // Handle nulls: null values go to the end
          if (aValue === null && bValue === null) return 0
          if (aValue === null) return 1
          if (bValue === null) return -1
          return aValue - bValue
        })
      }

      artistsStore.setArtists(sortedArtists)
      await sleep(100)
      reArrangeSortedArtists(fieldName)
    } finally {
      await sleep(1000)
      isSortingInProgress.value = false
    }
  }


  const setSort = (field: SortOption) => {
    let direction =
      activeSort.value.direction === SortDirection.ASC
        ? SortDirection.DESC
        : SortDirection.ASC

    if (activeSort.value.field !== field) {
      direction = SortDirection.ASC
    }

    activeSort.value = {
      field,
      direction
    }

    switch (field) {
      case SortOption.FIRSTNAME: {
        alphabetSort('firstname')
        break
      }
      case SortOption.SURNAME: {
        alphabetSort('surname') // as name in UI
        break
      }
      case SortOption.BORN: {
        numberSort('born')
        break
      }
      case SortOption.GENDER: {
        alphabetSort('gender')
        break
      }
      case SortOption.AUCTIONS_TURNOVER_2023_H1_USD: {
        numberSort('auctions_turnover_2023_h1_USD')
        break
      }
    }
  }

  return {
    SortDirection,
    SortOption,
    activeSort,
    setSort,
    isSortingInProgress
  }
})
