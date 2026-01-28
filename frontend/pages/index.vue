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
    <div class="menu-bg" />
    <div class="menu">
      <Sort />
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
import { useArtistsStore } from "~/J/useArtistsStore";
import { randomRange } from "~/J/useUtils";

const config = useRuntimeConfig();
const artistsStore = useArtistsStore();
const isTable = ref(true);

type ArtistPositionUpdate = { id: string; position: { x: number; y: number } }

const handleToggleTableAndBubbles = () => {
  isTable.value = !isTable.value
}

const handleArtistPositionUpdate = ({ id, position }: ArtistPositionUpdate) => {
  artistsStore.updateArtistPosition(id, position)
}

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
  position fixed
  display flex
  gap 2rem
  justify-content: center;
  left 0
  right 0
  top 0
  width 100%
  padding 1rem 0
  z-index var(--z-index-ui-controls)
.menu-bg
  position fixed
  top 0
  left 0
  right 0
  height 7rem
  z-index calc(var(--z-index-ui-controls) - 1)
  pointer-events none
  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 1) 0%,
    rgba(255, 255, 255, 1) 98%,
    rgba(255, 255, 255, 0) 100%
  )

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
  z-index var(--z-index-ui-controls)
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
