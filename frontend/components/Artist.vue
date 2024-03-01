<template>
  <div
    ref="artistRef"
    :class="['artist', {'artist__sorting-in-progress': useSortStore().isSortingInProgress}]"
    :style="handlePieceStyle"
    @click="openArtistModal(artistData)"
    @mousedown="handleOnMouseDown"
    @mousemove="mouseMoveHandler"
    @mouseleave="mouseLeaveHandler"
    @mouseup="mouseUpHandler"
    @touchmove="touchmoveHandler"
    @touchend="touchendHandler"
  >
    <img
      ref="artistProfileImage"
      class="artist__artwork-preview-image"
      :src="artistData.artworks[0].picture"
      :alt="artistData.name"
    />
    <svg
      class="artist__name-svg-circle"
      viewBox="0 0 400 400"
      :style="randomizedRotation"
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
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  artistData: Artist
}>()
import interact from 'interactjs'
import useAritstModal from './useArtistModal'
const { openArtistModal } = useAritstModal()

import useMouseActionDetector from '~/J/useMouseActionDetector'
import { type Artist } from '../J/useArtistsStore'
const {
  mouseDownHandler,
  mouseMoveHandler,
  mouseUpHandler,
  mouseLeaveHandler,
  zIndexOfLastSelectedPiece,
  touchmoveHandler,
  touchendHandler
} = useMouseActionDetector()

const localZIndex = ref(1)
const artistRef = ref()

const randomRange = (min: number, max: number) => {
  return Math.floor(Math.random() * (max - min + 1) + min)
}

const randomizeRotation = () => {
  return {
    rotate: `${randomRange(0, 360)}deg`
  }
}
const randomizedRotation = computed(() => randomizeRotation())

onMounted(() => {
  interact(artistRef.value as any)
    .draggable({
      inertia: true,
      autoScroll: true,
      listeners: {
        move(event: any) {
          const xRaw = props.artistData.position.x + event.dx
          const yRaw = props.artistData.position.y + event.dy
          const x = xRaw > 0 ? xRaw : 0
          props.artistData.position.x = x
          props.artistData.position.y = yRaw
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
      inertia: true
    })
})

const handleOnMouseDown = () => {
  mouseDownHandler()
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

<style lang="stylus" scoped>
.artist
  position absolute

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
</style>
