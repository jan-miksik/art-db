<template>
  <div class="filter-option" @click="filterStore.setFilter(filterOption)">
        <span v-if="filterStore.activeFilter.field === filterOption">
          <!-- <span v-if="filterStore.activeFilter.direction === filterStore.FilterDirection.ASC
            ">
            △
          </span>
          <span v-else> ▼ </span> -->
        </span>
        {{ label || filterOption }}
        <span v-if="filterStore.activeFilter.field === filterOption">
          <!-- <span v-if="filterStore.activeFilter.direction === filterStore.FilterDirection.ASC
            ">
            △
          </span> -->
          <!-- <span v-else> ▼ </span> -->
        </span>
      </div>
</template>

<script setup lang="ts">
import type { FilterOption } from '#imports';

const props = defineProps<{
  filterOption: FilterOption
  label?: string
}>()
const filterStore = useFilterStore()

</script>

<style lang="stylus" scoped>
.filter-option
  width: 100%
  text-align: center
  line-height: 1.5rem
  z-index 10000000000
  &:hover
    background-color: black
    color: white
    cursor: pointer
</style>