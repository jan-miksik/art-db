<template>
    <teleport v-if="isOpen && artistData" to="body" >
    <div class="artist-modal" @click="closeModal">
      <!-- <div class="artist-modal__close">X</div> -->
      <h2 class="artist-modal__name" @click.stop>{{ artistData.name }}</h2>
      <div class="aritst-modal__profile" @click.stop>
        <img
        class="artist-modal__profile-image"
        :src="artistData.profile_image"
        :alt="artistData.name"
        @click.stop
        />
      </div>
      <img
        class="artist-modal__artwork-preview-image"
        :src="artistData.artworks[0].picture"
        :alt="artistData.name"
        @click.stop
      />
    </div>
  </teleport>
</template>

<script setup lang="ts">
import useAritstModal from "./useArtistModal";
const { isOpen, artistData } = useAritstModal();

const closeModal = () => {
  isOpen.value = false;
};

</script>

<style lang="stylus" scoped>
.artist-modal
  position fixed
  top 0
  left 0
  bottom 0
  right 0
  background-color #eeeeee
  z-index 10000000000
  display flex
  justify-content center
  align-items center
  cursor url('~/assets/close.svg'), auto

.artist-modal__close
  position absolute
  top 10px
  right 10px
  cursor pointer
  font-size 20px
  color red
  &:hover
    color darkred

.artist-modal__profile-image
  width 125px
  height 125px
  border-radius 50%
  object-fit cover
  object-position center
  // border 2px solid black
  filter: grayscale(1);
  cursor default

.aritst-modal__profile
  top 10px
  left 10px
  position absolute
  display flex
  align-items center
  cursor default
  // flex-direction: column;

.artist-modal__artwork-preview-image
  width: 80%;
  max-height: 65%;
  object-fit: contain;
  cursor default

.artist-modal__name
  background-color: #141414;
  color: white;
  position: absolute;
  top: 0;
  left: 160px;
  padding: 0.05rem 0.5rem;
  cursor default
</style>
