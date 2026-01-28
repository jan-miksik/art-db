import type { SortingState } from '@tanstack/vue-table'
import {
  GenderOptionEnum,
  MediaTypeOptionEnum,
} from '~/J/useFilterStore'

export { GenderOptionEnum, MediaTypeOptionEnum }

export type BornRangeFilter = {
  from: number | null
  to: number | null
}

export const isBornInRange = (born: number, range: BornRangeFilter): boolean => {
  if (range.from !== null && range.to !== null) {
    return born >= range.from && born <= range.to
  }
  if (range.from !== null) {
    return born >= range.from
  }
  if (range.to !== null) {
    return born <= range.to
  }
  return true
}

export const matchesGenderFilter = (
  gender: 'N' | 'W' | 'M',
  selected: GenderOptionEnum[]
): boolean => {
  if (!selected || selected.length === 0) return true

  return selected.some((option) => {
    if (option === GenderOptionEnum.NON_BINARY && gender === 'N') return true
    if (option === GenderOptionEnum.WOMAN && gender === 'W') return true
    if (option === GenderOptionEnum.MAN && gender === 'M') return true
    return false
  })
}

export const matchesMediaTypeFilter = (
  mediaTypes: ('nft' | 'digital' | 'painting' | 'sculpture')[],
  selected: MediaTypeOptionEnum[]
): boolean => {
  if (!selected || selected.length === 0) return true

  return selected.some((option) => {
    const mediaTypeLower = option.toLowerCase() as
      | 'nft'
      | 'digital'
      | 'painting'
      | 'sculpture'
    return mediaTypes.includes(mediaTypeLower)
  })
}

export const matchesIdFilter = (id: string, selected: string[]): boolean => {
  if (!selected || selected.length === 0) return true
  return selected.includes(String(id))
}

export const toggleSort = (
  current: SortingState,
  columnId: string
): SortingState => {
  const existing = current.find((sort) => sort.id === columnId)
  if (existing) {
    return [{ id: columnId, desc: !existing.desc }]
  }

  return [{ id: columnId, desc: false }]
}
