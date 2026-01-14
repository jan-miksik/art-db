<template>
  <img
    v-if="fullImageSrcComputed"
    :class="[{ 'image__full': !externalCssClass }, externalCssClass]"
    ref="fullImageRef"
    :loading="fullImageLoading"
    :fetchpriority="fullImageFetchpriority"
    :src="fullImageSrcComputed"
  />
  <div 
    v-else 
    ref="fullImageRef"
    :class="['anim-bg', { 'image__full': !externalCssClass }, externalCssClass]"
  />
</template>

<script setup lang="ts">
import { updateImage, addImage, getImage } from '~/services/idb'
import ImageFile from '~/models/ImageFile'
import { type ImageIDB } from '~/services/idb'

const props = defineProps<{
  imageFile: ImageFile
  externalCssClass?: string | string[] | Record<string, boolean> | Array<string | Record<string, boolean>>
}>()
const { externalCssClass } = toRefs(props)

const imageFileComputed = computed(() => props.imageFile)

const isVisible = ref(false)


const fullImageSrc = ref('')
const fullImageFileInIDB = ref<ImageIDB>()
const fullImageRef = ref()
const isFullImageLoaded = ref(false)
const blobUrlRef = ref<string | null>(null)
let observer: IntersectionObserver | null = null


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
  // return imageFileComputed.value.url
  return fullImageSrc.value
})

const handleSetupMissingImage = () => {
  // Create an SVG with black background as a data URL
  const blackSvg = `data:image/svg+xml;charset=utf-8,<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 100 100"><rect width="100%" height="100%" fill="black"/></svg>`
  fullImageSrc.value = blackSvg
  fullImageRef.value?.classList.remove('anim-bg')
}


const giveFullImageSourcePlease = async () => {

  if (fullImageSrc.value || fullImageFileInIDB.value) return
  if (!props.imageFile.url) {
    handleSetupMissingImage()
    return
  }
  
  fullImageFileInIDB.value = await getImage(imageFileComputed.value.url)

  if (!fullImageFileInIDB.value) {
    addImage(imageFileComputed.value)
    if (blobUrlRef.value) {
      URL.revokeObjectURL(blobUrlRef.value)
      blobUrlRef.value = null
    }
    fullImageSrc.value = imageFileComputed.value.url
    return
  }

  if (fullImageFileInIDB.value) {
    if (fullImageFileInIDB.value.lastUpdated !== imageFileComputed.value.lastUpdated) {
      updateImage(imageFileComputed.value)
      if (blobUrlRef.value) {
        URL.revokeObjectURL(blobUrlRef.value)
        blobUrlRef.value = null
      }
      fullImageSrc.value = imageFileComputed.value.url
      return
    }
    if (blobUrlRef.value) {
      URL.revokeObjectURL(blobUrlRef.value)
      blobUrlRef.value = null
    }
    blobUrlRef.value = URL.createObjectURL(fullImageFileInIDB.value.blob)
    fullImageSrc.value = blobUrlRef.value
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
  fullImageRef.value?.addEventListener('load', loadedFullImage)

  observer = new IntersectionObserver((entries) => {
    // The callback will be called when the image enters or leaves the viewport
    if (entries[0].isIntersecting) {
      // The image has entered the viewport
      isVisible.value = true
      // We don't need the observer anymore, so we disconnect it
      observer?.disconnect()
    }
  }, {
    threshold: 0
  })

  // Start observing the image
  if (fullImageRef.value) {
    observer.observe(fullImageRef.value)
  }
})


onUnmounted(() => {
  // Clean up event listener
  fullImageRef.value?.removeEventListener('load', loadedFullImage)
  // Clean up IntersectionObserver to prevent memory leaks
  observer?.disconnect()
  observer = null
  if (blobUrlRef.value) {
    URL.revokeObjectURL(blobUrlRef.value)
    blobUrlRef.value = null
  }
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
