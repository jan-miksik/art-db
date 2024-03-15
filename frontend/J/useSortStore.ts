import { useArtistsStore } from './useArtistsStore'

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
  const activeSort = ref<{
    field: SortOption | null
    direction: SortDirection | null
  }>({
    field: null,
    direction: null
  })

  const isSortingInProgress = ref(false)

  const sleep = async (ms: number) => {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  const reArangeSortedArtists = (fieldName: 'firstname' | 'surname' | 'born' | 'gender' | 'auctions_turnover_2023_h1_USD') => {
    let topPosition = 200
    useArtistsStore().artists.forEach((artist, index) => {
      if (index === 0) {
        artist.position.y = topPosition
      }

      if (index > 0 && useArtistsStore().artists[index - 1][fieldName] === artist[fieldName]) {
        artist.position.y = topPosition
        return
      }
      
      if (index > 0) {
        if (artist.position.y + 120 < topPosition) {
          artist.position.y = topPosition + 120
          topPosition = topPosition + 120
        } else if (artist.position.y + 350 > topPosition) {
          artist.position.y = topPosition + 120
          topPosition = topPosition + 120
        } else {
          topPosition = artist.position.y
        }
      }
    })
  }

  const alphabetSort = async (fieldName: 'firstname' | 'surname' | 'gender') => {
    isSortingInProgress.value = true

    if (activeSort.value.direction === SortDirection.ASC) {
      useArtistsStore().artists.sort((a, b) => {
        return a[fieldName].localeCompare(b[fieldName])
      })
        await sleep(100)
        reArangeSortedArtists(fieldName)
    } else {
      useArtistsStore().artists.sort((a, b) => {
        return b[fieldName].localeCompare(a[fieldName])
      })
        await sleep(100)
        reArangeSortedArtists(fieldName)
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
      reArangeSortedArtists(fieldName)
    } else {
      useArtistsStore().artists.sort((a, b) => {
        return +a[fieldName] - +b[fieldName]
      })
      await sleep(100)
      reArangeSortedArtists(fieldName)
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
