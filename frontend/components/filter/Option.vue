<template>
  <div class="filter-option">
      <div class="filter-option__search" v-if="filterType === FilterType.SEARCH">
          {{ label || filterOption }} <input v-model="textToSearch" @input="handleSearchInputChange"/>
      </div>
      <div class="filter-option__range" v-if="filterType === FilterType.RANGE">
          {{ label || filterOption }} 
          
          <input class="filter-option__range-from" placeholder="" type="number" v-model="rangeFrom" @input="handleRangeChange"/> -
          <input class="filter-option__range-to" placeholder="" type="number" v-model="rangeTo" @input="handleRangeChange"/>
      </div>
    </div>
</template>

<script setup lang="ts">
import type { FilterOption, FilterType } from '#imports';

const textToSearch = ref('')
const rangeFrom = ref('')
const rangeTo = ref('')

const handleSearchInputChange = () => {
  emit('search', textToSearch.value)
}

const handleRangeChange = () => {
  emit('range', rangeFrom.value, rangeTo.value)
}

const props = defineProps<{
  filterOption: FilterOption
  label?: string
  filterType: FilterType
}>()
const filterStore = useFilterStore()

const emit = defineEmits<{
  (e: 'search', text: string): void
  (e: 'range', rangeFrom: string, rangeTo: string): void
}>()

</script>

<style lang="stylus" scoped>
.filter-option
  // width: 100%
  text-align: center
  line-height: 1.5rem
  z-index 10000000000
  // &:hover
  //   background-color: black
  //   color: white
  //   cursor: pointer

.filter-option__range
.filter-option__search
  display: flex
  gap 0.5rem

.filter-option__range-to
.filter-option__range-from
  width: 3rem;

</style>