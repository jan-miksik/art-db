<template>
  <div :class="['filter-option', `filter-option--${filterType}`]">
      <div class="filter-option__search" v-if="filterType === FilterType.SEARCH">
          <img src="~/assets/search.svg" height="20" alt="Search icon">
          <label for="filter-search-input" class="visually-hidden">Search by name</label>
          <input id="filter-search-input" v-model="textToSearch" class="filter-option__search-input" @input="handleSearchInputChange" placeholder=""/>
      </div>
      <div class="filter-option__range" v-if="filterType === FilterType.RANGE">
          {{ label || filterOption }}
          <input class="filter-option__range-from" placeholder="min" type="number" v-model="rangeFrom" @input="handleRangeChange"/> -
          <input class="filter-option__range-to" placeholder="max" type="number" v-model="rangeTo" @input="handleRangeChange"/>
      </div>
      <div class="filter-option__selection" v-if="filterType === FilterType.SELECTION">
        <div v-for="(selectionOption) in selectionOptions" @click="() => handleSelectionChange(selectionOption)" :class="['filter-option__selection-option', {'filter-option__selection-option--is-selected': isOptionSelected(selectionOption)}]">
          <!-- {{ selectionOption.sign }} -->
          <img v-if="selectionOption.sign" :src="selectionOption.sign" height="16"/>
        </div>
      </div>
      <div class="filter-option__selection" v-if="filterType === FilterType.SELECTION_TEXT">
        <div v-for="(selectionOption) in selectionOptions" @click="() => handleSelectionChange(selectionOption)" :class="['filter-option__selection-option-text-container', {'filter-option__selection-option--is-selected': isOptionSelected(selectionOption)}]">
          <span class="filter-option__selection-option-text" v-if="selectionOption.text">{{ selectionOption.text }}</span>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import type { FilterOption, SelectionOptionType } from '#imports';
import { FilterType } from '~/J/useFilterStore';
const filterStore = useFilterStore()
const { textToSearch, rangeFrom, rangeTo } = storeToRefs(filterStore)

const props = defineProps<{
  filterOption: FilterOption
  label?: string
  filterType: FilterType
  selectionOptions?: SelectionOptionType<any>[]
  selectedOptions?: SelectionOptionType<any>[]
}>()

const emit = defineEmits<{
  (e: 'search', text: string): void
  (e: 'range', rangeFrom: string, rangeTo: string): void
  (e: 'selection', selectedOption?: SelectionOptionType<any>): void
}>()


const handleSearchInputChange = () => {
  emit('search', textToSearch.value)
}

const handleRangeChange = () => {
  emit('range', rangeFrom.value, rangeTo.value)
}

const handleSelectionChange = (selectionOption: SelectionOptionType<any>) => {
  emit('selection', selectionOption)
}

const isOptionSelected = (selectionOption: SelectionOptionType<any>) => {
  return props.selectedOptions?.some((selectedOption) => selectedOption.enumValue === selectionOption.enumValue)
}

</script>

<style lang="stylus" scoped>
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

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
  width 5rem

.filter-option
  text-align: center
  line-height: 1.5rem
  z-index 10000000000

.filter-option__selection
  display: flex
  gap 0.5rem
  font-size: 1.2rem

.filter-option__selection-option-text-container
  opacity: 0.35
  cursor: pointer
  padding: 2px;

.filter-option__selection-option-text
  border 1px solid gray
  border-radius: 5px
  padding: 4px 6px;
  font-family 'Roboto', sans-serif
  cursor: pointer
  font-size: 14px
  &:hover
    background-color: #b0b0b0

.filter-option__selection-option
  opacity: 0.2
  cursor: pointer
  padding: 2px;
  height: 20px;
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
  background: transparent;

</style>
