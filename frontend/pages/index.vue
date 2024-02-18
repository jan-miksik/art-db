<template>
  <div>
    <Artist
      v-for="artist in artists"
      :key="artist.id"
      :artist-data="artist"
      class="artist"
      />
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

</script>

<style lang="stylus" scoped>
.artist
  position absolute
</style>
