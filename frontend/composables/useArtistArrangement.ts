import { useArtistsStore } from '~/J/useArtistsStore'

/**
 * Composable for arranging artists in the UI
 */
export const useArtistArrangement = () => {
  const artistsStore = useArtistsStore()

  /**
   * Rearranges sorted artists vertically based on a field name
   * @param fieldName - The field name to use for grouping (e.g., 'firstname', 'surname', 'born', etc.)
   */
  const reArrangeSortedArtists = (
    fieldName: 'firstname' | 'surname' | 'born' | 'gender' | 'auctions_turnover_2023_h1_USD'
  ) => {
    let topPosition = 200
    artistsStore.artists.forEach((artist, index) => {
      if (index === 0) {
        artist.position.y = topPosition
      }

      if (index > 0 && artistsStore.artists[index - 1][fieldName] === artist[fieldName]) {
        artist.position.y = topPosition
        return
      }

      if (index > 0) {
        if (artist.position.y + 120 < topPosition) {
          artist.position.y = topPosition + 120
          topPosition = topPosition + 120
        } else if (artist.position.y + 350 > topPosition) {
          artist.position.y = topPosition + 120
          topPosition = topPosition + 120
        } else {
          topPosition = artist.position.y
        }
      }
    })
  }

  return {
    reArrangeSortedArtists
  }
}
