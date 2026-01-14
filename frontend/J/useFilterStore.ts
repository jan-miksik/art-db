import { useArtistsStore } from './useArtistsStore'

export enum FilterOption {
  'NAME',
  'BORN',
  'GENDER',
  'AUCTIONS_TURNOVER_2023_H1_USD',
  'MEDIA_TYPE',
}

export enum FilterType {
  SEARCH = 'SEARCH',
  RANGE = 'RANGE',
  SELECTION = 'SELECTION',
  SELECTION_TEXT = 'SELECTION_TEXT',
}

export enum GenderOptionEnum {
  NON_BINARY = "NON_BINARY",
  MAN = "MAN",
  WOMAN = "WOMAN",
}

export enum MediaTypeOptionEnum {
  PAINTING = "PAINTING",
  NFT = "NFT",
  DIGITAL = "DIGITAL",
  SCULPTURE = "SCULPTURE",
}

export type SelectionOptionType<T> = {
  text?: string,
  sign?: string,
  enumValue: T
}

import FluidSvg from '~/assets/fluid.svg'
import FemalePng from '~/assets/female.png'
import MalePng from '~/assets/male.png'

export const useFilterStore = defineStore('filter', () => {

  const selectedGendersToShow = ref<SelectionOptionType<GenderOptionEnum>[]>([])
  const selectedMediaToShow = ref<SelectionOptionType<MediaTypeOptionEnum>[]>([])
  const isFilterByBornInRange = ref(false)
  const isFilterByName = ref(false)
  const isFilteringInProgress = ref(false)
  const selectedArtistForSearchSimilar = ref<Artist>()
  const isFilterByGender = computed(() => selectedGendersToShow.value.length > 0)
  const isFilterByMediaType = computed(() => selectedMediaToShow.value.length > 0)
  const textToSearch = ref('')
  const rangeFrom = ref('')
  const rangeTo = ref('')
  const isShowSimilarAuthors = ref(false)
  const hasFilters = computed(() =>
      rangeFrom.value ||
      rangeTo.value ||
      textToSearch.value ||
      isFilterByGender.value ||
      isShowSimilarAuthors.value ||
      isFilterByMediaType.value ||
      isFilterByMediaType.value
  )

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

  const mediaTypeOptions = [
    {
      text: 'painting',
      enumValue: MediaTypeOptionEnum.PAINTING
    },
    {
      text: 'nft',
      enumValue: MediaTypeOptionEnum.NFT
    },
    {
      text: 'sculpture',
      enumValue: MediaTypeOptionEnum.SCULPTURE
    },
  ]

  const reArrangeSortedArtists = (fieldName: 'firstname') => {
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

  const applyAllFilters = async () => {
    isFilteringInProgress.value = true;
    let filteredResults = [...useArtistsStore().artistsAll];

    if (textToSearch.value) {
      const searchTextLower = textToSearch.value.toLowerCase();
      filteredResults = filteredResults.filter(person => 
        person.name.toLowerCase().includes(searchTextLower)
      );
    }

    if (rangeFrom.value || rangeTo.value) {
      const from = Number(rangeFrom.value);
      const to = Number(rangeTo.value);
      
      filteredResults = filteredResults.filter(person => {
        if (from && !to) return person.born >= from;
        if (!from && to) return person.born <= to;
        if (from && to) return person.born >= from && person.born <= to;
        return true;
      });
    }

    if (selectedGendersToShow.value.length > 0) {
      filteredResults = filteredResults.filter(person =>
        selectedGendersToShow.value.some(option => {
          if (option.enumValue === GenderOptionEnum.NON_BINARY && person.gender === 'N') return true;
          if (option.enumValue === GenderOptionEnum.WOMAN && person.gender === 'W') return true;
          if (option.enumValue === GenderOptionEnum.MAN && person.gender === 'M') return true;
          return false;
        })
      );
    }

    if (selectedMediaToShow.value.length > 0) {
      filteredResults = filteredResults.filter(person =>
        selectedMediaToShow.value.some(option => {
          if (option.enumValue === MediaTypeOptionEnum.PAINTING && person.media_types.includes('painting')) return true;
          if (option.enumValue === MediaTypeOptionEnum.NFT && person.media_types.includes('nft')) return true;
          if (option.enumValue === MediaTypeOptionEnum.DIGITAL && person.media_types.includes('digital')) return true;
          if (option.enumValue === MediaTypeOptionEnum.SCULPTURE && person.media_types.includes('sculpture')) return true;
          return false;
        })
      );
    }

    useArtistsStore().setArtists(filteredResults);
    await sleep(100);
    reArrangeSortedArtists('firstname');
    isFilteringInProgress.value = false;
  }

  const searchAndFilterByName = async (whatToSearch: string) => {
    textToSearch.value = whatToSearch;
    isFilterByName.value = !!whatToSearch;
    await applyAllFilters();
  }

  const filterByBornInRange = async (from: string, to: string) => {
    rangeFrom.value = from;
    rangeTo.value = to;
    isFilterByBornInRange.value = !!(from || to);
    await applyAllFilters();
  }

  const filterByMediaType = async (selectedMediaType?: SelectionOptionType<MediaTypeOptionEnum>) => {
    if (!selectedMediaType) {
      return;
    }
    if (selectedMediaToShow.value.some((option) => option.enumValue === selectedMediaType.enumValue)) {
      selectedMediaToShow.value = selectedMediaToShow.value.filter(o => o.enumValue !== selectedMediaType.enumValue);
    } else {
      selectedMediaToShow.value.push(selectedMediaType);
    }
    await applyAllFilters();
  }

  const filterByGender = async (selectedGender?: SelectionOptionType<GenderOptionEnum>) => {
    if (!selectedGender) {
      return;
    }
    if (selectedGendersToShow.value.some((option) => option.enumValue === selectedGender.enumValue)) {
      selectedGendersToShow.value = selectedGendersToShow.value.filter(o => o.enumValue !== selectedGender.enumValue);
    } else {
      selectedGendersToShow.value.push(selectedGender);
    }
    await applyAllFilters();
  }

  const filterByIds = async (ids: number[]) => {
    isFilteringInProgress.value = true;

    const filteredPeople = ids.map(id => useArtistsStore().artistsAll.find(artist => +artist.id === +id)) as Artist[];

    useArtistsStore().setArtists(filteredPeople);
    await sleep(100)
    reArrangeSortedArtists('firstname');
  }

  const removeFilters = async () => {
    selectedGendersToShow.value = [];
    selectedMediaToShow.value = [];
    selectedArtistForSearchSimilar.value = undefined;
    textToSearch.value = '';
    rangeFrom.value = '';
    rangeTo.value = '';
    isShowSimilarAuthors.value = false;
    await applyAllFilters();
  }

  return {
    filterByIds,
    FilterOption,
    FilterType,
    searchAndFilterByName,
    filterByBornInRange,
    filterByGender,
    filterByMediaType,
    removeFilters,
    isFilteringInProgress,
    genderOptions,
    mediaTypeOptions,
    selectedGendersToShow,
    selectedMediaToShow,
    selectedArtistForSearchSimilar,
    hasFilters,
    textToSearch,
    rangeFrom,
    rangeTo,
    isShowSimilarAuthors,
  }
})
