import { describe, it, expect } from 'vitest'
import {
  isBornInRange,
  matchesGenderFilter,
  matchesMediaTypeFilter,
  matchesIdFilter,
  toggleSort,
  GenderOptionEnum,
  MediaTypeOptionEnum,
} from '~/J/artistsTableUtils'

describe('artistsTableUtils', () => {
  describe('isBornInRange', () => {
    it('returns true when no bounds are set', () => {
      expect(isBornInRange(1980, { from: null, to: null })).toBe(true)
    })

    it('filters by lower bound only', () => {
      expect(isBornInRange(1970, { from: 1980, to: null })).toBe(false)
      expect(isBornInRange(1990, { from: 1980, to: null })).toBe(true)
    })

    it('filters by upper bound only', () => {
      expect(isBornInRange(1970, { from: null, to: 1960 })).toBe(false)
      expect(isBornInRange(1950, { from: null, to: 1960 })).toBe(true)
    })

    it('filters by inclusive range', () => {
      expect(isBornInRange(1980, { from: 1970, to: 1985 })).toBe(true)
      expect(isBornInRange(1960, { from: 1970, to: 1985 })).toBe(false)
    })
  })

  describe('matchesGenderFilter', () => {
    it('allows all when no gender is selected', () => {
      expect(matchesGenderFilter('N', [])).toBe(true)
    })

    it('matches selected genders', () => {
      expect(matchesGenderFilter('N', [GenderOptionEnum.NON_BINARY])).toBe(true)
      expect(matchesGenderFilter('M', [GenderOptionEnum.WOMAN])).toBe(false)
    })
  })

  describe('matchesMediaTypeFilter', () => {
    it('allows all when no media types are selected', () => {
      expect(matchesMediaTypeFilter(['painting'], [])).toBe(true)
    })

    it('matches any selected media type', () => {
      expect(
        matchesMediaTypeFilter(['nft', 'digital'], [
          MediaTypeOptionEnum.SCULPTURE,
          MediaTypeOptionEnum.NFT,
        ])
      ).toBe(true)
      expect(
        matchesMediaTypeFilter(['painting'], [MediaTypeOptionEnum.DIGITAL])
      ).toBe(false)
    })
  })

  describe('matchesIdFilter', () => {
    it('allows all when no ids are provided', () => {
      expect(matchesIdFilter('10', [])).toBe(true)
    })

    it('matches when id exists in the list', () => {
      expect(matchesIdFilter('5', ['5', '6'])).toBe(true)
      expect(matchesIdFilter('7', ['5', '6'])).toBe(false)
    })
  })

  describe('toggleSort', () => {
    it('adds ascending sort when no sorting is set', () => {
      expect(toggleSort([], 'born')).toEqual([{ id: 'born', desc: false }])
    })

    it('toggles direction when same column is sorted', () => {
      const current = [{ id: 'born', desc: false }]
      expect(toggleSort(current, 'born')).toEqual([{ id: 'born', desc: true }])
    })

    it('resets to ascending when different column is sorted', () => {
      const current = [{ id: 'born', desc: true }]
      expect(toggleSort(current, 'surname')).toEqual([
        { id: 'surname', desc: false },
      ])
    })
  })
})

