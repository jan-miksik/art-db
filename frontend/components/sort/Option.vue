<template>
  <div class="sort-option" @click="sortStore.setSort(sortOption)">
        <span v-if="sortStore.activeSort.field === sortOption && isSortSignBeforeText">
          <span v-if="sortStore.activeSort.direction === sortStore.SortDirection.ASC
            ">
            △
          </span>
          <span v-else> ▼ </span>
        </span>
        {{ label || sortOption }}
        <span v-if="sortStore.activeSort.field === sortOption && !isSortSignBeforeText">
          <span v-if="sortStore.activeSort.direction === sortStore.SortDirection.ASC
            ">
            △
          </span>
          <span v-else> ▼ </span>
        </span>
      </div>
</template>

<script setup lang="ts">
import type { SortOption } from '#imports';

const props = defineProps<{
  sortOption: SortOption
  label?: string
  isSortSignBeforeText?: boolean
}>()
const sortStore = useSortStore()

</script>

<style lang="stylus" scoped>
.sort-option
  width: 100%
  text-align: center
  line-height: 1.5rem
  z-index 10000000000
  &:hover
    background-color: black
    color: white
    cursor: pointer
</style>
