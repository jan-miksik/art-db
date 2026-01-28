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
    
    let topPosition = INITIAL_Y_POSITION
    
    artistsStore.artists.forEach((artist, index) => {
      // Ensure position object exists
      if (!artist.position) {
        artist.position = { x: 0, y: 0 }
      }

      if (index === 0) {
        // First artist: set initial position
        artist.position.y = topPosition
        return
      }

      const previousArtist = artistsStore.artists[index - 1]
      if (!previousArtist) return
      const hasSameFieldValue = previousArtist[fieldName] === artist[fieldName]

      if (hasSameFieldValue) {
        // Group artists with the same field value at the same Y position
        artist.position.y = topPosition
        // Don't update topPosition - keep them grouped together
        return
      }

      // Artists with different field values: always position at proper spacing
      // This ensures consistent spacing regardless of initial random positions
      artist.position.y = topPosition + ARTIST_SPACING
      topPosition = topPosition + ARTIST_SPACING
    })
  }

  return {
    reArrangeSortedArtists
  }
}
