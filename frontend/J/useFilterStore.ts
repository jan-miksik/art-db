import { useArtistsStore } from './useArtistsStore'

export enum FilterOption {
  'NAME',
  'BORN',
  'GENDER',
  'AUCTIONS_TURNOVER_2023_H1_USD'
}

export enum FilterType {
  SEARCH = 'SEARCH',
  RANGE = 'RANGE',
  SELECTION = 'SELECTION',
}

export enum GenderOptionEnum {
  NON_BINARY = "NON_BINARY",
  MAN = "MAN",
  WOMAN = "WOMAN",
}

export type SelectionOptionType = {
  sign: string,
  enumValue: GenderOptionEnum
}

import FluidSvg from '~/assets/fluid.svg'
import FemalePng from '~/assets/female.png'
import MalePng from '~/assets/male.png'

export const useFilterStore = defineStore('filter', () => {

  const genderOptions = [
    {
      sign: FluidSvg,
      enumValue: GenderOptionEnum.NON_BINARY
    },
    {
      sign: MalePng,
      enumValue: GenderOptionEnum.MAN
    },
    {
      sign: FemalePng,
      enumValue: GenderOptionEnum.WOMAN
    },
  ]

  const isFilteringInProgress = ref(false)
  const selectedGendersToShow = ref<SelectionOptionType[]>([])

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

  const filterByGender = async (selectedGender: SelectionOptionType) => {
    isFilteringInProgress.value = true;
    if (selectedGendersToShow.value.some((option) => option.enumValue === selectedGender.enumValue)) {
      selectedGendersToShow.value = selectedGendersToShow.value.filter(o => o.enumValue !== selectedGender.enumValue)
    } else {
      selectedGendersToShow.value.push(selectedGender)
    }
    
    const filteredPeople = useArtistsStore().artistsAll.filter(person => {
      return selectedGendersToShow.value.some(option => {
        if (option.enumValue === GenderOptionEnum.NON_BINARY && person.gender === 'N') {
          return true;
        }
        if (option.enumValue === GenderOptionEnum.WOMAN && person.gender === 'W') {
          return true;
        }
        if (option.enumValue === GenderOptionEnum.MAN && person.gender === 'M') {
          return true;
        }
        return false;
      });
    });
    useArtistsStore().artists = filteredPeople;
    await sleep(100)
    reArangeSortedArtists('firstname');
  }

  const filterByIds = async (ids: string[]) => {
    isFilteringInProgress.value = true;
    
    const filteredPeople = useArtistsStore().artistsAll.filter(person => {
      if (ids.includes(person.id)) return true
      return false
    });
    useArtistsStore().artists = filteredPeople;
    await sleep(100)
    reArangeSortedArtists('firstname');
  }

  const removeFilters = () => {
    useArtistsStore().artists = useArtistsStore().artistsAll
  }

  return {
    filterByIds,
    FilterOption,
    FilterType,
    searchAndFilterByName,
    filterByBornInRange,
    filterByGender,
    removeFilters,
    isFilteringInProgress,
    genderOptions,
    selectedGendersToShow,
    // genderOptionEnumsArray,
  }
})
