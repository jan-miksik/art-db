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
}

export const useArtistsStore = defineStore('artists', () => {
  const artists = ref<Artist[]>([])
  console.log('artists: ', artists);

  // watch(() => artists.value[0].position, () => {
  //   console.log('artists: ', artists.value);
  //   console.log('artists changed')
  
  // }, {deep: true, immediate: true})

  return {
    artists
  }
})
