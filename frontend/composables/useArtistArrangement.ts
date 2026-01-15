import { useArtistsStore } from '~/J/useArtistsStore'

/**
 * Composable for arranging artists in the UI
 */
export const useArtistArrangement = () => {
  const artistsStore = useArtistsStore()

  /**
   * Rearranges sorted artists vertically based on a field name
   * Groups artists with the same field value at the same Y position,
   * and spaces artists with different values 120px apart vertically.
   * @param fieldName - The field name to use for grouping (e.g., 'firstname', 'surname', 'born', etc.)
   */
  const reArrangeSortedArtists = (
    fieldName: 'firstname' | 'surname' | 'born' | 'gender' | 'auctions_turnover_2023_h1_USD'
  ) => {
    const INITIAL_Y_POSITION = 200
    const ARTIST_SPACING = 120 // Vertical spacing between different groups
    const OVERLAP_THRESHOLD = 350 // Distance to check for overlapping artists
    
    let topPosition = INITIAL_Y_POSITION
    
    artistsStore.artists.forEach((artist, index) => {
      if (index === 0) {
        // First artist: set initial position
        artist.position.y = topPosition
        return
      }

      const previousArtist = artistsStore.artists[index - 1]
      const hasSameFieldValue = previousArtist[fieldName] === artist[fieldName]

      if (hasSameFieldValue) {
        // Group artists with the same field value at the same Y position
        artist.position.y = topPosition
        // Don't update topPosition - keep them grouped together
        return
      }

      // Artists with different field values: ensure proper spacing
      const artistBottom = artist.position.y + ARTIST_SPACING
      const isArtistTooHigh = artistBottom < topPosition
      const isArtistOverlapping = artist.position.y < topPosition + OVERLAP_THRESHOLD

      if (isArtistTooHigh || isArtistOverlapping) {
        // Reposition artist below the previous group
        artist.position.y = topPosition + ARTIST_SPACING
        topPosition = topPosition + ARTIST_SPACING
      } else {
        // Artist is already in a good position, use it as the new reference
        topPosition = artist.position.y
      }
    })
  }

  return {
    reArrangeSortedArtists
  }
}
