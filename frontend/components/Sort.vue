<template>
  <div class="sort" ref="menuRef">
    <button 
      class="sort__toggle" 
      @click="toggleMenu"
      :aria-expanded="isOpenMenu"
      aria-controls="sort-menu"
      aria-label="Toggle sort menu"
      type="button"
    >
      <img src="~/assets/sort.svg" width="30" alt="Sort">
    </button>
    <div v-if="isOpenMenu" id="sort-menu" class="sort__menu" role="menu">
      <SortOptionComponent :sortOption="SortOption.SURNAME" label="name" class="name-sort" isSortSignBeforeText/>
      <SortOptionComponent :sortOption="SortOption.BORN" label="born" class="born-sort" isSortSignBeforeText/>
      <SortOptionComponent :sortOption="SortOption.AUCTIONS_TURNOVER_2023_H1_USD" label="auctions 2023" class="auctions-sort" :isSortSignBeforeText="false"/>
    </div>
  </div>
</template>

<script setup lang="ts">
import SortOptionComponent from '~/components/sort/Option.vue'

const menuRef = ref<HTMLElement>()
const isOpenMenu = ref(false)

const toggleMenu = () => {
  isOpenMenu.value = !isOpenMenu.value
}

const { SortOption } = useArtistsTable()

const handleClickOutside = (event: MouseEvent | TouchEvent) => {
  if (menuRef.value && !menuRef.value.contains(event.target as Node)) {
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
  z-index var(--z-index-ui-controls)
  background-color white


.sort__toggle
  top: 1rem;
  cursor pointer
  width: 8.1rem;
  z-index var(--z-index-ui-controls)
  text-align center
  font-family 'Roboto', sans-serif
  font-size 1.4rem
  font-weight 700
  display: flex;
  justify-content: center;
  background: none
  border: none
  padding: 0

.sort__toggel-reversed-v
  transform: rotate(180deg);
  // position: absolute;
  top: -0.1rem;

.sort__toggel-v
  // position: absolute;

.sort__menu
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 8.1rem;
  position relative

.sort__triangel-1
  position: absolute;
  top: 0.8rem;

.name-sort
  position absolute
  top: -30px;
  right: 93px;
  rotate 0deg
  padding-right: 0.5rem;
  text-align: end;
  width: 4rem;

.born-sort
  position absolute
  top: 5px;
  right: 65px;
  padding-right: 0.5rem;
  rotate: 0deg;
  text-align: end;
  width: 4rem;

.auctions-sort
  position absolute
  top: -24px;
  left: 90px;
  rotate: 0deg;
  padding-left: 0.5rem;
  text-align: start;
</style>
