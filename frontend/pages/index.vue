<template>
  <div>
    <Sort />
    <!-- <Filter /> -->
    <Artist
      v-for="artist in artists"
      :key="artist.id"
      :artist-data="artist"
      class="artist"
      />
      <ArtistModal />
  </div>
</template>

<script setup lang="ts">
import axios from "axios";
const artists = ref<any>([]);
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
      artists.value = response.data;
      artists.value.forEach((artist: any) => {
        artist.position = randomizePosition();
      });
      useArtistsStore().artists = artists.value;
    })
    .catch((error) => console.error("Error:", error));

});

</script>

<style lang="stylus" scoped>
.artist
  position absolute
</style>
