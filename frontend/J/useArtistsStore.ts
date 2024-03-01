export type Artist = {
  profile_image: string
  name: string
  surname: string
  firstname: string
  notes: string
  born: number
  artworks: {
    picture: string
  }[]
  position: {
    x: number
    y: number
  }
  gender: string
  auctions_turnover_2023_h1_USD: number
}

export const useArtistsStore = defineStore('artists', () => {
  const artists = ref<Artist[]>([])
  console.log('artists: ', artists);

  return {
    artists
  }
})
