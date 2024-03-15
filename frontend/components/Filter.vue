<template>
  <div ref="menuRef">
    <div class="filter" @click="toggleMenu"><img src="~/assets/filter.png" width="50"></div>

    <div v-if="isOpenMenu" class="filter__menu">
      <FilterOption :filterOption="filterStore.FilterOption.SURNAME" label="name"/>
      <FilterOption :filterOption="filterStore.FilterOption.BORN" label="born"/>
      <!-- <FilterOption :filterOption="filterStore.FilterOption.GENDER" label="gender"/> -->
      <FilterOption :filterOption="filterStore.FilterOption.AUCTIONS_TURNOVER_2023_H1_USD" label="auctions 2023"/>
    </div>
  </div>
</template>

<script setup lang="ts">
const menuRef = ref<HTMLElement>()
const isOpenMenu = ref(false)

const toggleMenu = () => {
  isOpenMenu.value = !isOpenMenu.value
}

const filterStore = useFilterStore()

const handleClickOutside = (event: any) => {
  if (menuRef.value && !menuRef.value.contains(event.target)) {
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
  position fixed
  top: 1rem;
  left: 35%;
  font-size: 1.2rem;
  cursor pointer
  transform: translate(-50%, 0);
  z-index 10000000000

.filter__menu
  position: fixed;
  display: flex;
  flex-direction: column;
  align-items: center;
  top: 3rem;
  left: 35%;
  width: 9rem;
  transform: translate(-50%, 0)
  z-index 10000000000

.filter__triangel-1
  position: absolute;
  top: 0.8rem;
</style>
