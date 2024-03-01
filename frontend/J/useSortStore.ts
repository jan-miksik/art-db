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

  const reArangeSortedArtists = () => {
    let topPosition = 200
    useArtistsStore().artists.forEach((artist, index) => {
      if (index === 0) {
        artist.position.y = topPosition
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

  const alphabetSort = (fieldName: 'firstname' | 'surname') => {
    isSortingInProgress.value = true

    if (activeSort.value.direction === SortDirection.ASC) {
      useArtistsStore().artists.sort((a, b) => {
        return a[fieldName].localeCompare(b[fieldName])
      })
      reArangeSortedArtists()
    } else {
      useArtistsStore().artists.sort((a, b) => {
        return b[fieldName].localeCompare(a[fieldName])
      })
      reArangeSortedArtists()
    }
    setTimeout(() => {
      isSortingInProgress.value = false
    }, 1000)
  }

  const numberSort = (fieldName: 'born') => {
    isSortingInProgress.value = true

    if (activeSort.value.direction === SortDirection.ASC) {
      useArtistsStore().artists.sort((a, b) => {
        return b[fieldName] - a[fieldName]
      })
      reArangeSortedArtists()
    } else {
      useArtistsStore().artists.sort((a, b) => {
        return a[fieldName] - b[fieldName]
      })
      reArangeSortedArtists()
    }
    setTimeout(() => {
      isSortingInProgress.value = false
    }, 1000)
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
