<template>
  <div>
    <img
      class="artist__profile-image"
      :src="artistData.artworks[0].picture"
      :alt="artistData.name"
      ref="artistProfileImage"
    />
    <svg
      class="artist__name-svg-circle"
      viewBox="0 0 400 400"
      :style="randomizeRotation()"
    >
      <defs>
        <path
          d="M0, 200a200, 200 0 1, 0 400, 0a200, 200 0 1, 0 -400, 0"
          id="txt-path"
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
  profile_image: string;
  name: string;
  notes: string;
};

const props = defineProps<{
  artistData: Artist;
}>();
console.log('artistData: ', props.artistData);
const artistProfileImage = ref();
const randomRange = (min: number, max: number) => {
  return Math.floor(Math.random() * (max - min + 1) + min);
};

const randomizeRotation = () => {
  return {
    rotate: `${randomRange(0, 360)}deg`,
  };
};

// onMounted(() => {
  
//   artistProfileImage.value?.addEventListener('mouseenter', () => {

//     console.log('mouseenter');
//     console.log('props.artistData.profile_image: ', props.artistData.profile_image);
//     artistProfileImage.value.style.cursor = `url(${props.artistData.profile_image}), auto`;
//   });
  
//   artistProfileImage.value?.addEventListener('mouseleave', () => {
//     artistProfileImage.value.style.cursor = 'default';  
//   });
// })
</script>

<style lang="stylus" scoped>
.artist__profile-image
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: contain;
  z-index: 10;
  transition 0.3s ease-in-out
  position: relative;

  &:hover
    border-radius: 40%;
    cursor: pointer;


// @keyframes rotating {
//   from {
//     transform: rotate(0deg);
//   }
//   to {
//     transform: rotate(360deg);
//   }
// }

.artist__name-svg-circle
  translate: -129px -10px;
  width: 139px;
  position: absolute;

.artist__name-text
  font-size: 25px
  font-family: "Helvetica Neue"
  font-weight: 300
  letter-spacing: 5px
  position: relative;
</style>
