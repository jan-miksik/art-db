<template>
  <div ref="menuRef">
    <div class="sort" @click="toggleMenu">△▼△▼△</div>

    <div v-if="isOpenMenu" class="sort__menu">
      <SortOption :sortOption="sortStore.SortOption.SURNAME" label="name"/>
      <SortOption :sortOption="sortStore.SortOption.BORN" label="born"/>
      <!-- <SortOption :sortOption="sortStore.SortOption.GENDER" label="gender"/> -->
      <SortOption :sortOption="sortStore.SortOption.AUCTIONS_TURNOVER_2023_H1_USD" label="auctions 2023"/>
    </div>
  </div>
</template>

<script setup lang="ts">
const menuRef = ref<HTMLElement>()
const isOpenMenu = ref(false)

const toggleMenu = () => {
  isOpenMenu.value = !isOpenMenu.value
}

const sortStore = useSortStore()

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
.sort
  position fixed
  top: 1rem;
  left: 50%;
  font-size: 1.2rem;
  cursor pointer
  transform: translate(-50%, 0);
  z-index 10000000000

.sort__menu
  position: fixed;
  display: flex;
  flex-direction: column;
  align-items: center;
  top: 3rem;
  left: 50%;
  width: 9rem;
  transform: translate(-50%, 0)
  z-index 10000000000

.sort__triangel-1
  position: absolute;
  top: 0.8rem;
</style>
