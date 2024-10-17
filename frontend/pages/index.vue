<template>
  <div>
      <Filter />
    <div class="menu">
<!--      <SearchImageByAI/>-->
      <Sort />
<!--      <img src="~/assets/clear.svg" alt="clear" />-->
      <div v-if="hasClearButton" class="clear-button" @click="handleClear">
        <img src="~/assets/close.svg" width="16" :class="['filter-toggle-img']">
      </div>

      <div class="toggle-table-and-bubbles" @click="handleToggleTableAndBubbles">
        {{ isTable ? 'bubbles' : 'table' }}
      </div>
    </div>
    <ArtistsTable v-if="isTable"/>
    <Artist
      v-else
      v-for="artist in useArtistsStore().artists"
      :key="artist.id"
      :artist-data="artist"
      class="artist"
      />

    <ArtistModal />
  </div>
</template>

<script setup lang="tsx">
import axios from "axios";

const config = useRuntimeConfig();
const filterStore = useFilterStore()
const isTable = ref(true)

const handleToggleTableAndBubbles = () => {
  isTable.value = !isTable.value
}

const randomRange = (min: number, max: number) => {
  return Math.floor(Math.random() * (max - min + 1) + min);
};

const hasClearButton = computed(() => {
  return useFilterStore().hasFilters;
});

const handleClear = () => {
  useFilterStore().removeFilters();
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
  display flex
  gap 2rem
  justify-content: center;
  width 100%

.clear-button
  position absolute
  left 50px
  top 28px
  cursor pointer
  padding 5px
  z-index: 10000000000
  &:hover
    color white
    background-color black

.toggle-table-and-bubbles
  position: absolute;
  right: 0;
  top: 5rem;
  cursor: pointer;
  padding: 5px;
  rotate: 90deg;
  text-transform: uppercase;
  font-family: sans-serif;
  &:hover
    color white
    background-color black
</style>
