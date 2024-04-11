<template>
  <div class="filter" ref="menuRef">
    <div class="filter-toggle" @click="toggleMenu">ϒ
      <!-- <img src="~/assets/filter.png" width="50"> -->
    </div>

    <div v-if="isOpenMenu" class="filter__menu">
      <FilterOption 
        :filterOption="filterStore.FilterOption.NAME" 
        label="name"
        @search="filterStore.searchAndFilterByName"
        :filterType="filterStore.FilterType.SEARCH"
      />
      <FilterOption 
        :filterOption="filterStore.FilterOption.BORN" 
        label="born" 
        @range="filterStore.filterByBornInRange"
        :filterType="filterStore.FilterType.RANGE"
      />
      <FilterOption 
        :filterOption="filterStore.FilterOption.GENDER" 
        :selectionOptions="filterStore.genderOptions"
        :selectedOptions="filterStore.selectedGendersToShow"
        @selection="filterStore.filterByGender"
        :filterType="filterStore.FilterType.SELECTION"
      />
      <!-- <FilterOption :filterOption="filterStore.FilterOption.GENDER" label="gender"/> -->
      <!-- <FilterOption :filterOption="filterStore.FilterOption.AUCTIONS_TURNOVER_2023_H1_USD" label="auctions 2023"/> -->
    </div>
  </div>
</template>

<script setup lang="ts">
const menuRef = ref<HTMLElement>()
const isOpenMenu = ref(false)

const toggleMenu = () => {
  isOpenMenu.value = !isOpenMenu.value
}

// const handleSearchName = (text: string) => {
//   console.log('handleSearchName text: ', text);
// }

const filterStore = useFilterStore()

const handleClickOutside = (event: any) => {
  if (menuRef.value && !menuRef.value.contains(event.target)) {
    isOpenMenu.value = false
  }
}

// onMounted(() => {
//   document.addEventListener('click', handleClickOutside)
// })

// onUnmounted(() => {
//   document.removeEventListener('click', handleClickOutside)
// })
</script>

<style lang="stylus" scoped>

::selection {
  color: black;
  background: white;
}
.filter
  display: flex;
  flex-direction: column;
  align-items: center;
  gap 0.5rem
  z-index 10000000000

.filter-toggle
  width: 8rem;
  font-weight 700
  font-size: 1.5rem;
  cursor pointer
  z-index 10000000000
  font-family 'Roboto', sans-serif
  text-align center

.filter__menu
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 8rem;
  gap 0.5rem

.filter__triangel-1
  position: absolute;
  top: 0.8rem;
</style>
