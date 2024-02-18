<template>
  <Artist v-for="artist in artists" :key="artist.id" :artistData="artist" :style="randomizePosition()" class="artist"/>
</template>

<script setup lang="ts">
import axios from 'axios';
const artists = ref<any>([]);
const config = useRuntimeConfig()

onMounted(async () => {
  axios.get(`${config.public.DJANGO_SERVER_URL}/artists/`)
    .then(response => {
      console.log('response: ', response);
      console.log('response.data: ', response.data);
      artists.value = response.data
    })
    .catch(error => console.error('Error:', error));
});

const generateRandomNumberPlusMinus = (max: number) => {
  return Math.floor((Math.random() * max + 1) * (Math.random() - 0.5) * 2)
}

const randomRange = (min: number, max: number) => {
  return Math.floor(Math.random() * (max - min + 1) + min)
}

const screenWidth = window.innerWidth
const screenHeight = window.innerHeight

const randomizePosition = () => {
  return {
    top: `${randomRange(100, screenHeight)-100}px`,
    left: `${randomRange(100, screenWidth)-139}px`,
  }
}

</script>

<style lang="stylus" scoped>
.artist 
  position absolute

</style>