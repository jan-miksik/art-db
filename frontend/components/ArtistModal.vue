<template>
    <teleport v-if="isOpen && artistData" to="body" >
    <div ref="modalRef" class="artist-modal" @click="closeModal">
       <div class="artist-modal__close"><img src="~/assets/close.svg" alt="close" width="30"> </div>
      <div class="artist-modal__name-and-show-similar">
        <h2 class="artist-modal__name" @click.stop>{{ artistData.name }}</h2>
      </div>
      <div class="artist-modal__profile" @click.stop>
        <BaseImage
          :image-file="{
            url: artistData.profile_image_url,
            lastUpdated: artistData.artworks[0].year
          }"
          :external-css-class="['artist-modal__profile-image']"
          @click.stop
        />
      </div>
      <div class="artist-modal__swiper-container">
        <div @click.stop class="artist-modal__swiper-inner-container">
        <swiper
          class="artist-modal__swiper"
          @click.stop
          :modules="[Navigation, Keyboard, Mousewheel]"
          :keyboard="{ enabled: true }"
          :slidesPerView="'auto'"
          :spaceBetween="50"
          :centeredSlides="true"
          @swiper="onSwiper"
          >
          <!-- @slideChange="handleOnSlideChange" -->
          <swiper-slide @click.stop class="artist-modal__slide" v-for="(piece, index) in artistData.artworks" :key="piece.title || index">
            <BaseImage
              :image-file="{
                url: piece.picture_url,
                lastUpdated: artistData.artworks[0].year
              }"
              :external-css-class="['artist-modal__artwork-preview-image', {'artist-modal__artwork-preview-image--swipe-on': artistData.artworks.length > 1}]"
            />
            <div class="artist-modal__artwork-description">
              {{ piece.title }}<span v-if="piece.year !== null">{{', ' + piece.year }}</span>
            </div>
          </swiper-slide>
        </swiper>
      </div>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import useArtistModal from "./useArtistModal";
const { isOpen, artistData } = useArtistModal();
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Navigation, Keyboard, Mousewheel } from 'swiper/modules';
import type { Swiper as SwiperType } from 'swiper'
import 'swiper/css';
import 'swiper/css/navigation';

const filterStore = useFilterStore()

const modalRef = ref<HTMLElement>()
const { activate: activateFocusTrap, deactivate: deactivateFocusTrap } = useFocusTrap(modalRef)

const swiperRef = ref<SwiperType>();
const closeModal = () => {
  isOpen.value = false;
}

watch([isOpen, () => artistData.value, modalRef], ([newIsOpen, , newRef]) => {
  if (newIsOpen && artistData.value && newRef) {
    nextTick(() => {
      if (modalRef.value) {
        activateFocusTrap()
      }
    })
  } else {
    // Deactivate when closing
    deactivateFocusTrap()
  }
})

onUnmounted(() => {
  deactivateFocusTrap()
})

const showSimilarAuthors = async () => {
  filterStore.isShowSimilarAuthors = true
  filterStore.selectedArtistForSearchSimilar = artistData.value
  const similarAuthors = artistData.value?.similar_authors_postgres_ids?.map((id: string) => +id)
  filterStore.filterByIds(similarAuthors || [])
  closeModal()
}

const onSwiper = (swiper: SwiperType) => {
  swiperRef.value = swiper
}

</script>

<style lang="stylus" scoped>
.artist-modal
  position fixed
  top 0
  left 0
  bottom 0
  right 0
  background-color #eeeeee
  z-index var(--z-index-modal)
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
  filter: grayscale(1);
  cursor default

.artist-modal__profile
  top 10px
  left 10px
  position absolute
  display flex
  align-items center
  cursor default

.artist-modal__artwork-preview-image
  width: 90%;
  max-height: 65%;
  object-fit: contain;
  cursor: default;
  &--swipe-on
    cursor: ew-resize;

.artist-modal__name
  background-color: #141414;
  color: white;
  padding: 0.05rem 0.5rem;
  cursor default

.artist-modal__swiper-container
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;

.artist-modal__swiper-inner-container
  height 60vh

.artist-modal__swiper
  overflow: visible;
  //cursor: ew-resize;
  height: 60vh;

.artist-modal__slide
  position relative
  display: flex;
  justify-content: center;
  align-items: center;
  width: fit-content;
  width: 55vw
  flex-direction: column;
  gap: 0.5rem;

.artist-modal__artwork-preview-image
  transition: opacity 0.3s;
  width: 100%;
  max-height: 100%;


.artist-modal__artwork-preview-image--active
  transition: opacity 0.3s;
  width: 100%;
  opacity 1

.artist-modal__artwork-description
  color: #212121;
  background: #ffffff;
  padding: 0.1rem 1rem;

.artist-modal__show-similar
  color black
  cursor pointer
  &:hover
    color #1fb001



.artist-modal__name-and-show-similar
  position: absolute;
  left: 160px;
  top: 0;
  display: flex;
  gap: 1rem;
  align-items: center;
  cursor default


</style>
