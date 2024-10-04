<template>
  <div class="filter" ref="menuRef">
      <FilterOption
        :filterOption="filterStore.FilterOption.NAME"
        label=""
        @search="filterStore.searchAndFilterByName"
        :filterType="filterStore.FilterType.SEARCH"
      />
    <div :class="['filter-toggle']" @click="toggleMenu">
      <!-- ϒ-->
      filter
<!--      <img src="~/assets/close.svg" width="20" :class="['filter-toggle-img',{'filter-toggle&#45;&#45;open': isOpenMenu}]">-->
    </div>

    <div v-if="isOpenMenu" class="filter__menu">
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
  position relative

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

.filter-toggle-img
  transition all 0.2s
  rotate 45deg

.filter-toggle--open
  rotate 0deg

.filter__menu
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 8rem;
  gap 0.5rem
  background-color: white;

.filter__triangel-1
  position: absolute;
  top: 0.8rem;
</style>
