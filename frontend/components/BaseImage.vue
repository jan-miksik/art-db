<template>
  <img
    :class="[{ 'image__full': !externalCssClass }, externalCssClass]"
    ref="fullImageRef"
    :loading="fullImageLoading"
    :fetchpriority="fullImageFetchpriority"
    :src="fullImageSrcComputed"
  />
</template>

<script setup lang="ts">
import { updateImage, addImage, getImage } from '~/services/idb'
import ImageFile from '~/models/ImageFile'
import { type ImageIDB } from '~/services/idb'

const props = defineProps<{
  imageFile: ImageFile
  externalCssClass?: any
}>()
const { imageFile, externalCssClass } = toRefs(props)

const isVisible = ref(false)


const fullImageSrc = ref('')
const fullImageFileInIDB = ref<ImageIDB>()
const fullImageRef = ref()
const isFullImageLoaded = ref(false)


const fullImageLoading = computed(() => {
  if (isVisible.value)
    return 'eager'
  return 'lazy'
})


const fullImageFetchpriority = computed(() => {
  if (isVisible.value)
    return 'high'
  return 'low'
})


const fullImageSrcComputed = computed(() => {
  // return imageFile.value.url
  return fullImageSrc.value
})


const giveFullImageSourcePlease = async () => {

  if (fullImageSrc.value || fullImageFileInIDB.value) return
  fullImageFileInIDB.value = await getImage(imageFile.value.url)

  if (!fullImageFileInIDB.value) {
    addImage(imageFile.value)
    fullImageSrc.value = imageFile.value.url
    return
  }

  if (fullImageFileInIDB.value) {
    if (fullImageFileInIDB.value.lastUpdated !== imageFile.value.lastUpdated) {
      updateImage(imageFile.value)
      fullImageSrc.value = imageFile.value.url
      return
    }

    fullImageSrc.value = URL.createObjectURL(fullImageFileInIDB.value.blob)
  }
}

const loadedFullImage = () => {
  fullImageRef.value?.classList.remove('anim-bg')
  isFullImageLoaded.value = true
}

watch(isVisible, (newVal) => {
  if (newVal) {
    giveFullImageSourcePlease()
  }
})

onMounted(async () => {

  fullImageRef.value?.classList.add('anim-bg')
  fullImageRef.value.addEventListener('load', loadedFullImage)

  const observer = new IntersectionObserver((entries) => {
    // The callback will be called when the image enters or leaves the viewport
    if (entries[0].isIntersecting) {
      // The image has entered the viewport
      isVisible.value = true
      // We don't need the observer anymore, so we disconnect it
      observer.disconnect()
    }
  }, {
    threshold: 0
  })

  // Start observing the image
  observer.observe(fullImageRef.value)
})


onUnmounted(() => {
  fullImageRef.value?.removeEventListener('load', loadedFullImage)
})

</script>

<style scoped lang="stylus">

.image__low
.image__full
  border 1px solid transparent
  position absolute
  object-fit contain
  width 100%
  left 0
  min-width 10px
  min-height 10px


.image__low
  z-index 10000000000

@keyframes background-color-palette
  0%
    background #f53b5a

  25%
    background #87ed69

  50%
    background #4c6ee6

  75%
    background #ffd97d

  100%
    background #644b6f

.anim-bg
  animation-name background-color-palette
  animation-duration 3.5s
  animation-iteration-count infinite
  animation-direction alternate

</style>
