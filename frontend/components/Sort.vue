<template>
  <div class="sort" ref="menuRef">
    <!-- <div class="sort__toggle" @click="toggleMenu">△▼△▼△</div> -->
    <div class="sort__toggle" @click="toggleMenu">V<snan class="sort__toggel-reversed-v">V</snan></div> 

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
  display: flex;
  flex-direction: column;
  align-items: center;
  gap 0.5rem
  z-index 10000000000


.sort__toggle
  top: 1rem;
  cursor pointer
  width: 8.1rem;
  z-index 10000000000
  text-align center
  font-family 'Roboto', sans-serif
  font-size 1.4rem
  font-weight 700

.sort__toggel-reversed-v
  transform: rotate(180deg);
  position: absolute;
  top: -0.1rem;

.sort__menu
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 8.1rem;

.sort__triangel-1
  position: absolute;
  top: 0.8rem;
</style>
