<template>
  <div>
    <div class="menu">
      <SearchImageByAI/>
      <Filter />
      <Sort />
    </div>
    <Artist
      v-for="artist in useArtistsStore().artists"
      :key="artist.id"
      :artist-data="artist"
      class="artist"
      />
      <ArtistModal />
  </div>
</template>

<script setup lang="ts">
import axios from "axios";
const config = useRuntimeConfig();

const randomRange = (min: number, max: number) => {
  return Math.floor(Math.random() * (max - min + 1) + min);
};

onMounted(async () => {
  const screenHeight = window.innerHeight;
  const screenWidth = window.innerWidth;
  const randomizePosition = () => {
  return {
  x: randomRange(100, screenWidth) - 139,
  y: randomRange(100, screenHeight) - 100,
  }
  };

  axios
    .get(`${config.public.DJANGO_SERVER_URL}/artists/`)
    .then((response) => {
      useArtistsStore().artistsAll = response.data;
      useArtistsStore().artists = response.data;
      useArtistsStore().artists.forEach((artist: any) => {
        artist.position = randomizePosition();
      });
      // useArtistsStore().artists = artists.value;
    })
    .catch((error) => console.error("Error:", error));

});

</script>

<style lang="stylus" scoped>
.artist
  position absolute

.menu
  position absolute
  position fixed
  display flex
  gap 2rem
  justify-content: center;
  width 100%

</style>
