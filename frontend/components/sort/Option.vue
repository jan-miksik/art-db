<template>
  <div class="sort-option" @click="handleClick">
        <span v-if="activeSort.field === sortOption && isSortSignBeforeText">
          <span v-if="activeSort.direction === SortDirection.ASC
            ">
            △
          </span>
          <span v-else> ▼ </span>
        </span>
        {{ label || sortOption }}
        <span v-if="activeSort.field === sortOption && !isSortSignBeforeText">
          <span v-if="activeSort.direction === SortDirection.ASC
            ">
            △
          </span>
          <span v-else> ▼ </span>
        </span>
      </div>
</template>

<script setup lang="ts">
import type { SortOption } from '~/J/useSortStore'
import { SortDirection } from '~/J/useSortStore'
import { useArtistsTable } from '~/J/useArtistsTable'

const props = defineProps<{
  sortOption: SortOption
  label?: string
  isSortSignBeforeText?: boolean
}>()
const { activeSort, setSort } = useArtistsTable()

const handleClick = () => {
  setSort(props.sortOption)
  if (typeof window !== 'undefined') {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

</script>

<style lang="stylus" scoped>
.sort-option
  width: 100%
  text-align: center
  line-height: 1.5rem
  z-index var(--z-index-ui-controls)
  &:hover
    background-color: black
    color: white
    cursor: pointer
</style>
