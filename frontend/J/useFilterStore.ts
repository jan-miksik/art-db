import { useArtistsStore } from './useArtistsStore'

export enum FilterOption {
  'FIRSTNAME',
  'SURNAME',
  'BORN',
  'GENDER',
  'AUCTIONS_TURNOVER_2023_H1_USD'
}

// export enum FilterDirection {
//   'ASC',
//   'DESC',
//   'ARRAY_WITH_ORDER'
// }

export const useFilterStore = defineStore('filter', () => {
  const activeFilter = ref<{
    field: FilterOption | null
    // direction: FilterDirection | null
  }>({
    field: null,
    // direction: null
  })

  const isFilteringInProgress = ref(false)

  const sleep = async (ms: number) => {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  const reArangeFilteredArtists = (fieldName: 'firstname' | 'surname' | 'born' | 'gender' | 'auctions_turnover_2023_h1_USD') => {
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

  const alphabetFilter = async (fieldName: 'firstname' | 'surname' | 'gender') => {
    isFilteringInProgress.value = true

    // if (activeFilter.value.direction === FilterDirection.ASC) {
    //   useArtistsStore().artists.filter((a, b) => {
    //     return a[fieldName].localeCompare(b[fieldName])
    //   })
    //     await sleep(100)
    //     reArangeFilteredArtists(fieldName)
    // } else {
    //   useArtistsStore().artists.filter((a, b) => {
    //     return b[fieldName].localeCompare(a[fieldName])
    //   })
    //     await sleep(100)
    //     reArangeFilteredArtists(fieldName)
    // }
    // setTimeout(() => {
    //   isFilteringInProgress.value = false
    // }, 1000)
  }

  const numberFilter = async (fieldName: 'born' | 'auctions_turnover_2023_h1_USD') => {
    isFilteringInProgress.value = true

    // if (activeFilter.value.direction === FilterDirection.ASC) {
    //   useArtistsStore().artists.filter((a, b) => {
    //     return +b[fieldName] - +a[fieldName]
    //   })
    //   await sleep(100)
    //   reArangeFilteredArtists(fieldName)
    // } else {
    //   useArtistsStore().artists.filter((a, b) => {
    //     return +a[fieldName] - +b[fieldName]
    //   })
    //   await sleep(100)
    //   reArangeFilteredArtists(fieldName)
    // }
    //   await sleep(1000)
    //   isFilteringInProgress.value = false
  }


  const setFilter = (field: FilterOption) => {
    // let direction =
    //   activeFilter.value.direction === FilterDirection.ASC
    //     ? FilterDirection.DESC
    //     : FilterDirection.ASC

    // if (activeFilter.value.field !== field) {
    //   direction = FilterDirection.ASC
    // }

    // activeFilter.value = {
    //   field,
    //   direction
    // }

    switch (field) {
      case FilterOption.FIRSTNAME: {
        alphabetFilter('firstname') 
        break
      }
      case FilterOption.SURNAME: {
        alphabetFilter('surname') // as name in UI
        break
      }
      case FilterOption.BORN: {
        numberFilter('born')
        break
      }
      case FilterOption.GENDER: {
        alphabetFilter('gender')
        break
      }
      case FilterOption.AUCTIONS_TURNOVER_2023_H1_USD: {
        numberFilter('auctions_turnover_2023_h1_USD')
        break
      }
    }
  }

  return {
    // FilterDirection,
    FilterOption,
    activeFilter,
    setFilter,
    isFilteringInProgress
  }
})
