<template>
  <div>
    <Artist
      v-for="artist in artists"
      :key="artist.id"
      :artist-data="artist"
      class="artist"
      />
      <!-- :style="randomizePosition()" -->
  </div>
</template>

<script setup lang="ts">
import axios from "axios";
const artists = ref<any>([]);
const config = useRuntimeConfig();

onMounted(async () => {

  axios
    .get(`${config.public.DJANGO_SERVER_URL}/artists/`)
    .then((response) => {

      console.log("response: ", response);
      console.log("response.data: ", response.data);
      artists.value = response.data;

})
    .catch((error) => console.error("Error:", error));

});

// const generateRandomNumberPlusMinus = (max: number) => {
//   return Math.floor((Math.random() * max + 1) * (Math.random() - 0.5) * 2);
// };

</script>

<style lang="stylus" scoped>
.artist
  position absolute
</style>
