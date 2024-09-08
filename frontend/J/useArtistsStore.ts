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
}

export const useArtistsStore = defineStore('artists', () => {
  const artists = ref<Artist[]>([])
  const artistsAll = ref<Artist[]>([])

  return {
    artists,
    artistsAll
  }
})
