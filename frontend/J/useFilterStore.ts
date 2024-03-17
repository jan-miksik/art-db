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

  const searchAndFilterByName = (whatToSearch: string) => {
    isFilteringInProgress.value = true;
    const searchTextLower = whatToSearch.toLowerCase();
    const filteredPeople = useArtistsStore().artistsAll.filter(person => {
      return person.name.toLowerCase().includes(searchTextLower);
    });
    useArtistsStore().artists = filteredPeople;
    isFilteringInProgress.value = false;
  }

  const filterByBornInRange = (from: number, to: number) => {
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

    isFilteringInProgress.value = false;

  }

  return {
    FilterOption,
    FilterType,
    searchAndFilterByName,
    filterByBornInRange,
    isFilteringInProgress
  }
})
