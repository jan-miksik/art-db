<template>
  <div>
      <Filter />
    <div v-if="artistsStore.error" class="error-message">
      {{ artistsStore.error }}
      <button @click="() => { artistsStore.error = null; }" class="error-close">×</button>
    </div>
    <div v-if="artistsStore.isLoading" class="loading-indicator">
      Loading artists...
    </div>
    <div class="menu">
      <Sort />
      <button v-if="hasClearButton" class="clear-button" @click="handleClear" aria-label="Clear filters">
        <img src="~/assets/close.svg" width="16" :class="['filter-toggle-img']">
      </button>

      <button class="toggle-table-and-bubbles" @click="handleToggleTableAndBubbles" :aria-label="`Switch to ${isTable ? 'bubbles' : 'table'} view`">
        {{ isTable ? 'bubbles' : 'table' }}
      </button>
    </div>
    <ArtistsTable v-if="isTable"/>
    <Artist
      v-else
      v-for="artist in artistsStore.artists"
      :key="artist.id"
      :artist-data="artist"
      @update-artist-position="handleArtistPositionUpdate"
      class="artist"
      />

    <ArtistModal />
  </div>
</template>

<script setup lang="tsx">
import { useFilterStore } from "~/J/useFilterStore";
import { useArtistsStore } from "~/J/useArtistsStore";
import { randomRange } from "~/composables/useUtils";

const config = useRuntimeConfig();
const filterStore = useFilterStore();
const artistsStore = useArtistsStore();
const isTable = ref(true);

type ArtistPositionUpdate = { id: string; position: { x: number; y: number } }

const handleToggleTableAndBubbles = () => {
  isTable.value = !isTable.value
}

const handleArtistPositionUpdate = ({ id, position }: ArtistPositionUpdate) => {
  artistsStore.updateArtistPosition(id, position)
}

const hasClearButton = computed(() => filterStore.hasFilters);

const handleClear = () => {
  filterStore.removeFilters();
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

  await artistsStore.fetchArtists(`${config.public.DJANGO_SERVER_URL}/artists/`);
  artistsStore.initializePositions(randomizePosition);
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
  z-index: var(--z-index-ui-controls)
  background: none
  border: none
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
  background: none
  border: none
  &:hover
    color white
    background-color black

.loading-indicator
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 1rem 2rem;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  border-radius: 4px;
  z-index: var(--z-index-loading);
  font-family: sans-serif;

.error-message
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 1rem 2rem;
  background-color: #ff4444;
  color: white;
  border-radius: 4px;
  z-index: var(--z-index-error);
  font-family: sans-serif;
  display: flex;
  align-items: center;
  gap: 1rem;
  max-width: 80%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);

.error-close
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  &:hover
    opacity: 0.8;
</style>
