<template>
  <div class="filter" ref="menuRef">
      <FilterOptionComponent
        :filterOption="FilterOption.NAME"
        label=""
        @search="searchAndFilterByName"
        :filterType="FilterType.SEARCH"
      />
    <button 
      :class="['filter-toggle']" 
      @click="toggleMenu"
      :aria-expanded="isOpenMenu"
      aria-controls="filter-menu"
      aria-label="Toggle filter menu"
      type="button"
    >
      filter
    </button>
    <button
      v-if="hasFilters"
      class="filter-clear"
      @click="removeFilters"
      aria-label="Clear filters"
      type="button"
    >
      <img src="~/assets/close.svg" width="16" class="filter-toggle-img">
    </button>

    <div v-if="isOpenMenu" id="filter-menu" class="filter__menu" role="menu">
      <FilterOptionComponent
        :filterOption="FilterOption.MEDIA_TYPE"
        :selectionOptions="mediaTypeOptions"
        :selectedOptions="selectedMediaToShow"
        @selection="handleMediaTypeSelection"
        :filterType="FilterType.SELECTION_TEXT"
      />
      <FilterOptionComponent
        :filterOption="FilterOption.GENDER"
        :selectionOptions="genderOptions"
        :selectedOptions="selectedGendersToShow"
        @selection="filterByGender"
        :filterType="FilterType.SELECTION"
      />
      <FilterOptionComponent
        :filterOption="FilterOption.BORN"
        label="born"
        @range="filterByBornInRange"
        :filterType="FilterType.RANGE"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import type { MediaTypeOptionEnum, SelectionOptionType } from '~/J/useFilterStore'
import { useArtistsTable } from '~/J/useArtistsTable'
import FilterOptionComponent from '~/components/filter/Option.vue'

const menuRef = ref<HTMLElement>()
const isOpenMenu = ref(false)

const toggleMenu = () => {
  isOpenMenu.value = !isOpenMenu.value
}

const {
  FilterOption,
  FilterType,
  mediaTypeOptions,
  genderOptions,
  selectedMediaToShow,
  selectedGendersToShow,
  searchAndFilterByName,
  filterByBornInRange,
  filterByGender,
  filterByMediaType,
  hasFilters,
  removeFilters,
} = useArtistsTable()

const handleMediaTypeSelection = (selectionOption?: SelectionOptionType<any>) => {
  if (!selectionOption) {
    return
  }

  filterByMediaType(selectionOption as SelectionOptionType<MediaTypeOptionEnum>)
}

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as Node | null
  if (menuRef.value && target && !menuRef.value.contains(target)) {
    isOpenMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style lang="stylus" scoped>

::selection {
  color: black;
  background: white;
}
.filter
  // Keep filter above the main menu so its toggle and menu stay clickable
  z-index calc(var(--z-index-ui-controls) + 1)
  position fixed

.filter-toggle
  font-weight 700
  font-size: 1.2rem;
  z-index var(--z-index-ui-controls)
  font-family 'Roboto', sans-serif
  text-align center
  transition all 0.3s
  position: absolute;
  top: 30px;
  left: 0;
  cursor url('~/assets/filter.svg'), pointer
  background: none
  border: none
  padding: 0

.filter-toggle-img
  transition all 0.2s

.filter-toggle--open
  rotate 0deg

.filter-clear
  position absolute
  left 50px
  top 28px
  cursor pointer
  padding 5px
  z-index var(--z-index-ui-controls)
  background: none
  border: none
  &:hover
    color white
    background-color black

.filter__menu
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-top: 2.5rem;
  width: fit-content;
  gap: 0.5rem;
  background-color: white;
  padding: 0 1rem 1rem 0;

.filter__triangel-1
  position: absolute;
  top: 0.8rem;
</style>
