<template>
  <div :class="['filter-option', `filter-option--${filterType}`]">
      <div class="filter-option__search" v-if="filterType === FilterType.SEARCH">
          <img src="~/assets/search.svg" height="20"><input v-model="textToSearch" class="filter-option__search-input" @input="handleSearchInputChange" placeholder="name"/>
      </div>
      <div class="filter-option__range" v-if="filterType === FilterType.RANGE">
          {{ label || filterOption }}
          <input class="filter-option__range-from" placeholder="min" type="number" v-model="rangeFrom" @input="handleRangeChange"/> -
          <input class="filter-option__range-to" placeholder="max" type="number" v-model="rangeTo" @input="handleRangeChange"/>
      </div>
      <div class="filter-option__selection" v-if="filterType === FilterType.SELECTION">
        <div v-for="(selectionOption) in selectionOptions" @click="() => handleSelectionChange(selectionOption)" :class="['filter-option__selection-option', {'filter-option__selection-option--is-selected': isOptionSelected(selectionOption)}]">
          {{ selectionOption.sign }}
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import type { FilterOption, FilterType, SelectionOptionType } from '#imports';

const props = defineProps<{
  filterOption: FilterOption
  label?: string
  filterType: FilterType
  selectionOptions?: SelectionOptionType[]
  selectedOptions?: SelectionOptionType[]
}>()

const textToSearch = ref('')
const rangeFrom = ref('')
const rangeTo = ref('')

const emit = defineEmits<{
  (e: 'search', text: string): void
  (e: 'range', rangeFrom: string, rangeTo: string): void
  (e: 'selection', selectedOption?: SelectionOptionType): void
}>()


const handleSearchInputChange = () => {
  emit('search', textToSearch.value)
}

const handleRangeChange = () => {
  emit('range', rangeFrom.value, rangeTo.value)
}

const handleSelectionChange = (selectionOption: SelectionOptionType) => {
  emit('selection', selectionOption)
}

const isOptionSelected = (selectionOption: SelectionOptionType) => {
  return props.selectedOptions?.some((selectedOption) => selectedOption.enumValue === selectionOption.enumValue)
}

</script>

<style lang="stylus" scoped>
input:focus {
    outline: none;
}

input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}

.filter-option__range-to
.filter-option__range-from
.filter-option__search-input
  border none
  border-bottom 1px solid #b0b0b0

  &:focus
    border-bottom 1px solid #000

.filter-option__search-input
  width 6.5rem

.filter-option
  text-align: center
  line-height: 1.5rem
  z-index 10000000000

.filter-option--SELECTION
  margin-right auto

.filter-option__selection
  display: flex
  gap 0.5rem
  font-size: 1.2rem

.filter-option__selection-option
  opacity: 0.2
  cursor: pointer
  &:hover
    background-color: #b0b0b0

.filter-option__selection-option--is-selected
  opacity 1

.filter-option__range
.filter-option__search
  display: flex
  gap 0.5rem



.filter-option__range-to
.filter-option__range-from
  width: 2rem;

</style>