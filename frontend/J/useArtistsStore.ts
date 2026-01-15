export type Artist = {
  id: string
  profile_image_url: string
  name: string
  surname: string
  firstname: string
  notes: string
  born: number
  artworks: {
    picture_url: string
    title: string
    year: number
    sizeY: number
    sizeX: number
  }[]
  position: {
    x: number
    y: number
  }
  gender: "W" | "M" | "N"
  auctions_turnover_2023_h1_USD: number
  similar_authors_postgres_ids: string[]
  media_types: ('nft' | 'digital' | 'painting' | 'sculpture')[]
}

export const useArtistsStore = defineStore('artists', () => {
  const artists = ref<Artist[]>([])
  const artistsAll = ref<Artist[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const fetchArtists = async (apiUrl: string) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await $fetch<{ success: boolean; data?: Artist[]; error?: string }>(apiUrl)
      
      if (!response?.success) {
        error.value = response?.error || 'Failed to load artists'
        console.error("Error: failed to load artists", response?.error)
        return
      }

      const fetchedArtists = response.data ?? []
      setArtistsAll(fetchedArtists)
      setArtists(fetchedArtists)
    } catch (err: unknown) {
      if (err instanceof Error && (err.name === 'AbortError' || (err as any).code === 'ECONNABORTED')) {
        error.value = "Request timed out. Please try again."
      } else if (err && typeof err === 'object' && ('status' in err || 'statusCode' in err)) {
        const status = (err as { status?: number; statusCode?: number }).status || (err as { status?: number; statusCode?: number }).statusCode
        const errData = (err as { data?: unknown }).data
        const dataMessage = errData ? `: ${typeof errData === 'string' ? errData : JSON.stringify(errData)}` : ''
        error.value = `Server error: ${status}${dataMessage}`
      } else if (err instanceof Error) {
        error.value = err.message
      } else {
        error.value = "An unknown error occurred. Please try again."
      }
      console.error("Error fetching artists:", err)
    } finally {
      isLoading.value = false
    }
  }

  const setArtists = (newArtists: Artist[]) => {
    artists.value = newArtists
  }

  const setArtistsAll = (newArtists: Artist[]) => {
    artistsAll.value = newArtists
  }

  const updateArtistPosition = (id: string, position: { x: number; y: number }) => {
    const updateInCollection = (collection: Artist[]) => {
      const artist = collection.find((item) => item.id === id)
      if (artist) {
        artist.position = { ...position }
      }
    }

    updateInCollection(artists.value)
    updateInCollection(artistsAll.value)
  }

  /**
   * Initializes positions for all artists using a provided function
   */
  const initializePositions = (randomizePositionFn: () => { x: number; y: number }) => {
    artists.value.forEach((artist) => {
      artist.position = randomizePositionFn()
    })
    // Also update artistsAll to keep them in sync
    artistsAll.value.forEach((artist) => {
      const matchingArtist = artists.value.find(a => a.id === artist.id)
      if (matchingArtist) {
        artist.position = { ...matchingArtist.position }
      } else {
        artist.position = randomizePositionFn()
      }
    })
  }

  return {
    // State
    artists,
    artistsAll,
    isLoading,
    error,
    // Actions
    fetchArtists,
    setArtists,
    setArtistsAll,
    updateArtistPosition,
    initializePositions,
  }
})
