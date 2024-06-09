<template>
    <teleport v-if="isOpen && artistData" to="body" >
    <div class="artist-modal" @click="closeModal">
       <div class="artist-modal__close"><img src="~/assets/close.svg" alt="close" width="30"> </div>
      <div class="artist-modal__name-and-show-similar">
        <h2 class="artist-modal__name" @click.stop>{{ artistData.name }}</h2>
        <span class="artist-modal__show-similar" @click.stop="showSimilarAuthors">show similar authors</span>
      </div>
      <div class="artist-modal__profile" @click.stop>
        <img
        class="artist-modal__profile-image"
        :src="artistData.profile_image_url"
        :alt="artistData.name"
        @click.stop
        />
      </div>
      <!-- <img v-for="(piece, index) in artistData.artworks"
        class="artist-modal__artwork-preview-image"
        :src="piece.picture_url"
        :alt="piece.title"
        @click.stop
      /> -->
      <div class="artist-modal__swiper-container">
        <div @click.stop class="artist-modal__swiper-inner-container">
        <!-- <div v-if="hasNextSlide" class="artist-modal__swiper-next-slide" @click="handleSwipeNext"/>
        <div v-if="hasPrevSlide" class="artist-modal__swiper-prev-slide" @click="handleSwipePrev"/> -->
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
          <swiper-slide @click.stop class="artist-modal__slide" v-for="(piece, index) in artistData.artworks">
            <img
              class='artist-modal__artwork-preview-image'
              :src="piece.picture_url"
              :alt="piece.title"
              @click.stop
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
import 'swiper/css';
import 'swiper/css/navigation';
import axios from "axios";

const filterStore = useFilterStore()
const config = useRuntimeConfig();

const swiperRef = ref();
const closeModal = () => {
  isOpen.value = false;
}

const similarAuthorsResult = ref([]);

const showSimilarAuthors = async () => {
  // filterStore.selectedArtistForSearchSimilar.value = null
  console.log('show similar authors', filterStore.selectedArtistForSearchSimilar);
  console.log('artistData.value?.artworks[0]', artistData.value)
  filterStore.selectedArtistForSearchSimilar = artistData.value
  try {
    const queryParams = new URLSearchParams({
      image_url: artistData.value?.artworks[0]?.picture_url ?? '',
      limit: '5',
    });
    const response = await axios.get(`${config.public.DJANGO_SERVER_URL}/artists/search-authors-by-image-url/?${queryParams.toString()}`);

    similarAuthorsResult.value = response.data
    const matchingIds = response.data.map((item: any) => item.author.id);
    filterStore.filterByIds(matchingIds)
    closeModal()
  } catch (error) {
    console.error(error)
  }
}

const onSwiper = (swiper: any) => {
  swiperRef.value = swiper
}

// const amountOfSlides = computed(() => {
//   return artistData.value?.artworks?.length || 0;
// });

// const hasNextSlide = computed(() => {
//   return activeIndex.value < amountOfSlides.value - 1;
// })
// const hasPrevSlide = computed(() => {
//   return activeIndex.value > 0 && amountOfSlides.value > 0;
// })
// const activeIndex = ref(0);

// const handleOnSlideChange = (swiper: any) => {
//   activeIndex.value = swiper?.activeIndex;
// }

// const handleSwipeNext = () => {
//   swiperRef.value.slideNext();
// }

// const handleSwipePrev = () => {
//   swiperRef.value.slidePrev();
// }

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
  cursor: ew-resize;
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

// .artist-modal__swiper-prev-slide
//   z-index: 10000000000;
//   position: absolute;
//   left: 0;
//   width: 150px;
//   height: inherit;
//   cursor url('~/assets/arrow-left.svg'), auto


// .artist-modal__swiper-next-slide
//   z-index: 10000000000;
//   position: absolute;
//   right: 0;
//   width: 150px;
//   height: inherit;
//   cursor url('~/assets/arrow-right.svg'), auto

</style>
