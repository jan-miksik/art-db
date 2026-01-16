<template>
  <button
    ref="artistRef"
    :class="['artist', {'artist__sorting-in-progress': !isDragging}]"
    :style="handlePieceStyle"
    @click="openArtistModal(artistData)"
    @mousedown="handleOnMouseDown"
    @mousemove="(e) => mouseMoveHandler(e)"
    @mouseleave="mouseLeaveHandler"
    @mouseup="mouseUpHandler"
    @touchmove="touchmoveHandler"
    @touchend="touchendHandler"
    :aria-label="`View details for ${artistData.name}`"
    type="button"
  >
    <BaseImage
      :image-file="{
        url: artistData.artworks?.[0]?.picture_url ?? ''
      }"
      :external-css-class="['artist__artwork-preview-image', { 'artist--is-selected-artist-for-search-similar': artistData?.id === useFilterStore().selectedArtistForSearchSimilar?.id}]"
      :alt="`Artwork preview for ${artistData.name}`"
    />
    <svg
      class="artist__name-svg-circle"
      viewBox="0 0 400 400"
      :style="randomizedRotation"
      :aria-label="`Artist name: ${artistData.name}`"
      role="img"
    >
      <defs>
        <path
          id="txt-path"
          d="M0, 200a200, 200 0 1, 0 400, 0a200, 200 0 1, 0 -400, 0"
        ></path>
      </defs>
      <text fill="black" class="artist__name-text">
        <textPath startOffset="12%" xlink:href="#txt-path">
          {{ artistData.name }}
        </textPath>
      </text>
    </svg>
  </button>
</template>

<script setup lang="ts">
import { useFilterStore } from '#imports'
import interact from 'interactjs'
import useArtistModal from './useArtistModal'
import useMouseActionDetector from '~/J/useMouseActionDetector'
import { type Artist } from '../J/useArtistsStore'
import { randomRange } from '~/composables/useUtils'

const { openArtistModal } = useArtistModal()
const props = defineProps<{
  artistData: Artist
}>()
const emit = defineEmits<{
  (e: 'update-artist-position', payload: { id: string; position: { x: number; y: number } }): void
}>()
const {
  isDragging,
  mouseDownHandler,
  mouseMoveHandler,
  mouseUpHandler,
  mouseLeaveHandler,
  zIndexOfLastSelectedPiece,
  touchmoveHandler,
  touchendHandler
} = useMouseActionDetector()

const localZIndex = ref(1)
const artistRef = ref<HTMLButtonElement | null>(null)

const randomizeRotation = () => {
  return {
    rotate: `${randomRange(0, 360)}deg`
  }
}
const randomizedRotation = ref(randomizeRotation())

onMounted(() => {
  if (artistRef.value) {
    interact(artistRef.value)
      .draggable({
        inertia: false,
        autoScroll: true,
        listeners: {
          move(event: { dx: number; dy: number }) {
            const x = Math.max(props.artistData.position.x + event.dx, 0)
            const y = Math.max(props.artistData.position.y + event.dy, 0)

            emit('update-artist-position', {
              id: props.artistData.id,
              position: { x, y }
            })
          }
        }
      })
      .resizable({
        // resize from edges and corners
        edges: { left: false, right: true, bottom: false, top: false },
        modifiers: [
          interact.modifiers.restrictSize({
            min: { width: 10, height: 10 }
          })
        ],
        inertia: false
      })
  }
})

onUnmounted(() => {
  // Clean up interact.js to prevent memory leaks
  if (artistRef.value) {
    interact(artistRef.value).unset()
  }
})

const handleOnMouseDown = (event: MouseEvent) => {
  mouseDownHandler(event)
  localZIndex.value = zIndexOfLastSelectedPiece.value
  zIndexOfLastSelectedPiece.value++
}

const handlePieceStyle = computed(() => {
  return {
    left: `${props.artistData?.position?.x || 0}px`,
    top: `${props.artistData?.position?.y || 0}px`,
    zIndex: `${localZIndex.value}`
  }
})
</script>

<style lang="stylus">
.artist
  position absolute
  background: none
  border: none
  padding: 0
  cursor: pointer

.artist__sorting-in-progress
  transition all 1s ease-in-out

.artist__artwork-preview-image
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: contain;
  z-index: 10;
  transition 0.1s ease-in-out
  position: relative;
  border: 2px solid transparent;

  &:hover
    border: 2px solid black;
    cursor: pointer;

.artist__name-svg-circle
  translate: -133px -10px;
  width: 142px;
  position: absolute;

.artist__name-text
  font-size: 25px;
  font-family: "Helvetica Neue";
  font-weight: 300;
  letter-spacing: 5px;
  position: relative

.artist--is-selected-artist-for-search-similar
  border 2px solid red
</style>
