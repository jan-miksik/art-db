<template>
  <div
    ref="artistRef"
    class="artist"
    :style="handlePieceStyle"
    @mousedown="handleOnMouseDown"
    @mousemove="mouseMoveHandler"
    @mouseleave="mouseLeaveHandler"
    @mouseup="mouseUpHandler"
    @touchmove="touchmoveHandler"
    @touchend="touchendHandler">
    <img
      ref="artistProfileImage"
      class="artist__profile-image"
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
type Artist = {
  profile_image: string
  name: string
  notes: string
  artworks: {
    picture: string
  }[]
}

const props = defineProps<{
  artistData: Artist
}>();
console.log("artistData: ", props.artistData);
import interact from "interactjs";
import useMouseActionDetector from "~/J/useMouseActionDetector";
const {
  mouseDownHandler,
  mouseMoveHandler,
  mouseUpHandler,
  mouseLeaveHandler,
  isDragging,
  zIndexOfLastSelectedPiece,
  touchmoveHandler,
  touchendHandler
} = useMouseActionDetector();

const localZIndex = ref(1);
const artistRef = ref()
const artistPosition = ref({
  position: {
    x: 0,
    y: 0,
    // deg: 0
  }
});
const randomRange = (min: number, max: number) => {

  return Math.floor(Math.random() * (max - min + 1) + min);

};

const randomizeRotation = () => {
  return {
    rotate: `${randomRange(0, 360)}deg`
  };
};
const randomizedRotation = ref(() => randomizeRotation());

onMounted(() => {
  const randomRange = (min: number, max: number) => {

  return Math.floor(Math.random() * (max - min + 1) + min);

  };

  const screenWidth = window.innerWidth;
  const screenHeight = window.innerHeight;

  const randomizePosition = () => {
    artistPosition.value.position = {
      x: randomRange(100, screenWidth) - 139,
      y: randomRange(100, screenHeight) - 100,
    }
  };
  randomizePosition();

  interact(artistRef.value as any)
    .draggable({
      inertia: true,
      autoScroll: true,
      listeners: {
        move(event: any) {

          // console.log('draggable event: ', event)
          // if (!isOnAdminPage.value) return
          // const scale = mapperEventData.value.scale
          // piece.value.isPublished = false
          const xRaw = artistPosition.value.position.x + event.dx;
          // console.log("xRaw: ", xRaw);
          const yRaw = artistPosition.value.position.y + event.dy;
          // console.log("yRaw: ", yRaw);
          // const x = xRaw > -2000 ? xRaw : -2000;
          // const y = yRaw > -2000 ? yRaw : -2000;
          artistPosition.value.position.x = xRaw;
          artistPosition.value.position.y = yRaw;
      },
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
    });

});

const handleOnMouseDown = () => {

  mouseDownHandler();
  localZIndex.value = zIndexOfLastSelectedPiece.value;
  zIndexOfLastSelectedPiece.value++;

};

const handlePieceStyle = computed(() => {
  return {
    left: `${artistPosition.value?.position?.x || 0}px`,
    top: `${artistPosition.value?.position?.y || 0}px`,
    zIndex: `${localZIndex.value}`
  };

})

</script>

<style lang="stylus" scoped>
.artist
  position absolute
.artist__profile-image
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
