<template>
  <div class="filter" ref="menuRef">
      <FilterOption
        :filterOption="filterStore.FilterOption.NAME"
        label=""
        @search="filterStore.searchAndFilterByName"
        :filterType="filterStore.FilterType.SEARCH"
      />
    <button 
      :class="['filter-toggle']" 
      @click="toggleMenu"
      :aria-expanded="isOpenMenu"
      aria-controls="filter-menu"
      aria-label="Toggle filter menu"
      type="button"
    >
      <!-- ϒ-->
      filter
      <!--      <img src="~/assets/close.svg" width="20" :class="['filter-toggle-img',{'filter-toggle&#45;&#45;open': isOpenMenu}]">-->
    </button>

    <div v-if="isOpenMenu" id="filter-menu" class="filter__menu" role="menu">
      <FilterOption
        :filterOption="filterStore.FilterOption.MEDIA_TYPE"
        :selectionOptions="filterStore.mediaTypeOptions"
        :selectedOptions="filterStore.selectedMediaToShow"
        @selection="handleMediaTypeSelection"
        :filterType="filterStore.FilterType.SELECTION_TEXT"
      />
      <FilterOption
        :filterOption="filterStore.FilterOption.GENDER"
        :selectionOptions="filterStore.genderOptions"
        :selectedOptions="filterStore.selectedGendersToShow"
        @selection="filterStore.filterByGender"
        :filterType="filterStore.FilterType.SELECTION"
      />
      <FilterOption
        :filterOption="filterStore.FilterOption.BORN"
        label="born"
        @range="filterStore.filterByBornInRange"
        :filterType="filterStore.FilterType.RANGE"
      />


      <!-- <FilterOption :filterOption="filterStore.FilterOption.AUCTIONS_TURNOVER_2023_H1_USD" label="auctions 2023"/> -->
    </div>
  </div>
</template>

<script setup lang="ts">
import type { MediaTypeOptionEnum, SelectionOptionType } from '~/J/useFilterStore'
const menuRef = ref<HTMLElement>()
const isOpenMenu = ref(false)

const toggleMenu = () => {
  isOpenMenu.value = !isOpenMenu.value
}

const filterStore = useFilterStore()

const handleMediaTypeSelection = (selectionOption?: SelectionOptionType<any>) => {
  if (!selectionOption) {
    return
  }

  filterStore.filterByMediaType(selectionOption as SelectionOptionType<MediaTypeOptionEnum>)
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
  z-index 10000000000
  position absolute

.filter-toggle
  font-weight 700
  font-size: 1.2rem;
  z-index 10000000000
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
  rotate 45deg

.filter-toggle--open
  rotate 0deg

.filter__menu
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-top: 2.5rem;
  width: fit-content;
  gap: 0.5rem;
  background-color: white;

.filter__triangel-1
  position: absolute;
  top: 0.8rem;
</style>
