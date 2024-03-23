import { useArtistsStore } from './useArtistsStore'

export enum FilterOption {
  'NAME',
  'BORN',
  'GENDER',
  'AUCTIONS_TURNOVER_2023_H1_USD'
}

export enum FilterType {
  'SEARCH',
  'RANGE',
  'SELECTION',
}

export const useFilterStore = defineStore('filter', () => {

  const isFilteringInProgress = ref(false)

  const reArangeSortedArtists = (fieldName: 'firstname') => {
    console.log('reArangeSortedArtists: ');
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

  const sleep = async (ms: number) => {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  const searchAndFilterByName = async (whatToSearch: string) => {
    isFilteringInProgress.value = true;
    const searchTextLower = whatToSearch.toLowerCase();
    const filteredPeople = useArtistsStore().artistsAll.filter(person => {
      return person.name.toLowerCase().includes(searchTextLower);
    });
    useArtistsStore().artists = filteredPeople;
    await sleep(100)
    reArangeSortedArtists('firstname');
  }

  const filterByBornInRange = async (from: number, to: number) => {
    isFilteringInProgress.value = true;

    const filteredPeople = useArtistsStore().artistsAll.filter(person => {
      if (from === 0 || isNaN(to) || !to || from > to) {
        return person.born >= from;
      }
      if (to === 0 || isNaN(to) || !from) {
        return person.born <= to;
      }
      return person.born >= from && person.born <= to;
    });

    useArtistsStore().artists = filteredPeople;
    await sleep(100)
    reArangeSortedArtists('firstname');
  }

  return {
    FilterOption,
    FilterType,
    searchAndFilterByName,
    filterByBornInRange,
    isFilteringInProgress
  }
})
