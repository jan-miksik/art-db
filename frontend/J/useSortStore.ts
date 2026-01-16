import { useArtistsStore } from './useArtistsStore'
import { sleep } from '~/composables/useUtils'
import { useArtistArrangement } from '~/composables/useArtistArrangement'

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

    if (activeSort.value.direction === SortDirection.ASC) {
      useArtistsStore().artists.sort((a, b) => {
        return a[fieldName].localeCompare(b[fieldName])
      })
        await sleep(100)
        reArrangeSortedArtists(fieldName)
    } else {
      useArtistsStore().artists.sort((a, b) => {
        return b[fieldName].localeCompare(a[fieldName])
      })
        await sleep(100)
        reArrangeSortedArtists(fieldName)
    }
    setTimeout(() => {
      isSortingInProgress.value = false
    }, 1000)
  }

  const numberSort = async (fieldName: 'born' | 'auctions_turnover_2023_h1_USD') => {
    isSortingInProgress.value = true

    if (activeSort.value.direction === SortDirection.ASC) {
      useArtistsStore().artists.sort((a, b) => {
        return +b[fieldName] - +a[fieldName]
      })
      await sleep(100)
      reArrangeSortedArtists(fieldName)
    } else {
      useArtistsStore().artists.sort((a, b) => {
        return +a[fieldName] - +b[fieldName]
      })
      await sleep(100)
      reArrangeSortedArtists(fieldName)
    }
      await sleep(1000)
      isSortingInProgress.value = false
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
