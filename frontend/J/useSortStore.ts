import { useArtistsStore } from './useArtistsStore'

export enum SortOption {
  'FIRSTNAME',
  'SURNAME',
  'BORN'
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

  const reArangeSortedArtists = (fieldName: 'firstname' | 'surname' | 'born') => {
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

  const alphabetSort = async (fieldName: 'firstname' | 'surname') => {
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

  const numberSort = async (fieldName: 'born') => {
    isSortingInProgress.value = true

    if (activeSort.value.direction === SortDirection.ASC) {
      useArtistsStore().artists.sort((a, b) => {
        return b[fieldName] - a[fieldName]
      })
      await sleep(100)
      reArangeSortedArtists(fieldName)
    } else {
      useArtistsStore().artists.sort((a, b) => {
        return a[fieldName] - b[fieldName]
      })
      await sleep(100)
      reArangeSortedArtists(fieldName)
    }
      await sleep(1000)
      isSortingInProgress.value = false
  }

  const sortByFirstName = () => {
    alphabetSort('firstname')
  }

  const sortBySurname = () => {
    alphabetSort('surname')
  }

  const sortByBorn = () => {
    numberSort('born')
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
        sortByFirstName()
        break
      }
      case SortOption.SURNAME: {
        sortBySurname()
        break
      }
      case SortOption.BORN: {
        sortByBorn()
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
