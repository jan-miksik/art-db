<template>
  <div ref="menuRef">
    <div class="sort" @click="toggleMenu">△▼△▼△</div>

    <div v-if="isOpenMenu" class="sort__menu">
      <div class="sort__menu-item" 
      @click="sortStore.setSort(sortStore.SortOption.FIRSTNAME)">
    <span v-if="sortStore.activeSort.field === sortStore.SortOption.FIRSTNAME">
      <span v-if="sortStore.activeSort.direction === sortStore.SortDirection.ASC">
        △
      </span>
      <span v-else>
        ▼
      </span>
    </span>
      firstname
      <span v-if="sortStore.activeSort.field === sortStore.SortOption.FIRSTNAME">
      <span v-if="sortStore.activeSort.direction === sortStore.SortDirection.ASC">
        △
      </span>
      <span v-else>
        ▼
      </span>
    </span>

    </div>

    <div class="sort__menu-item"
      @click="sortStore.setSort(sortStore.SortOption.SURNAME)">
      <span v-if="sortStore.activeSort.field === sortStore.SortOption.SURNAME">
      <span v-if="sortStore.activeSort.direction === sortStore.SortDirection.ASC">
        △
      </span>
      <span v-else>
        ▼
      </span>
    </span>
      surname
    <span v-if="sortStore.activeSort.field === sortStore.SortOption.SURNAME">
      <span v-if="sortStore.activeSort.direction === sortStore.SortDirection.ASC">
        △
      </span>
      <span v-else>
        ▼
      </span>
    </span>
    </div>
      
    <div class="sort__menu-item"
      @click="sortStore.setSort(sortStore.SortOption.BORN)">
      
      <span v-if="sortStore.activeSort.field === sortStore.SortOption.BORN">
      <span v-if="sortStore.activeSort.direction === sortStore.SortDirection.ASC">
        △
      </span>
      <span v-else>
        ▼
      </span>
    </span>
    born
    <span v-if="sortStore.activeSort.field === sortStore.SortOption.BORN">
      <span v-if="sortStore.activeSort.direction === sortStore.SortDirection.ASC">
        △
      </span>
      <span v-else>
        ▼
      </span>
    </span>
    </div>
      <!-- <div class="sort__menu-item">gender</div> -->
    </div>
  </div>
</template>

<script setup lang="ts">
const menuRef = ref<HTMLElement>();
const isOpenMenu = ref(false);

const toggleMenu = () => {
  isOpenMenu.value = !isOpenMenu.value;
};

const sortStore = useSortStore();

const handleClickOutside = (event: any) => {
  if (menuRef.value && !menuRef.value.contains(event.target)) {
    isOpenMenu.value = false;
  }
};

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside);
});

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
  width: 7rem;
  transform: translate(-50%, 0)
  z-index 10000000000

.sort__triangel-1
  position: absolute;
  top: 0.8rem;

.sort__menu-item
  width: 100%
  text-align: center
  line-height: 1.5rem
  z-index 10000000000
  &:hover
    background-color: black
    color: white
    cursor: pointer

</style>