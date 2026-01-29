<template>
  <img
    v-if="fullImageSrcComputed"
    :class="[{ 'image__full': !externalCssClass }, externalCssClass]"
    ref="imageRef"
    :loading="fullImageLoading"
    :fetchpriority="fullImageFetchpriority"
    :src="fullImageSrcComputed"
    :alt="alt"
  />
  <div 
    v-else 
    ref="placeholderRef"
    :class="['anim-bg', { 'image__full': !externalCssClass }, externalCssClass]"
  />
</template>

<script setup lang="ts">
import { updateImage, addImage, getImage } from '~/services/idb'
import { type IImageFile } from '~/models/ImageFile'
import { type ImageIDB } from '~/services/idb'

type CachedImageEntry = {
  src: string
  lastUpdated?: number
  isBlob: boolean
}

const imageSrcCache = new Map<string, CachedImageEntry>()
const DEBUG_IMAGE_CACHE =
  import.meta.env?.DEV === true ||
  (typeof window !== 'undefined' && window.localStorage?.getItem('debug-images') === '1')

const getCachedImage = (url: string, lastUpdated?: number): CachedImageEntry | null => {
  const cached = imageSrcCache.get(url)
  if (!cached) return null
  if (cached.lastUpdated && lastUpdated && cached.lastUpdated !== lastUpdated) {
    if (cached.isBlob) {
      URL.revokeObjectURL(cached.src)
    }
    imageSrcCache.delete(url)
    return null
  }
  return cached
}

const setCachedImage = (url: string, entry: CachedImageEntry) => {
  const existing = imageSrcCache.get(url)
  if (existing?.isBlob && existing.src !== entry.src) {
    URL.revokeObjectURL(existing.src)
  }
  imageSrcCache.set(url, entry)
}

const props = defineProps<{
  imageFile: IImageFile
  externalCssClass?: string | string[] | Record<string, boolean> | Array<string | Record<string, boolean>>
  alt?: string
}>()
const { externalCssClass } = toRefs(props)

const imageFileComputed = computed(() => props.imageFile)

const isVisible = ref(false)


const fullImageSrc = ref('')
const fullImageFileInIDB = ref<ImageIDB>()
const imageRef = ref<HTMLImageElement | null>(null)
const placeholderRef = ref<HTMLDivElement | null>(null)
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
  return fullImageSrc.value
})

const handleSetupMissingImage = () => {
  // Create an SVG with black background as a data URL
  const blackSvg = `data:image/svg+xml;charset=utf-8,<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 100 100"><rect width="100%" height="100%" fill="black"/></svg>`
  fullImageSrc.value = blackSvg
  imageRef.value?.classList.remove('anim-bg')
  placeholderRef.value?.classList.remove('anim-bg')
}


const currentImageUrl = ref<string>('')

const giveFullImageSourcePlease = async () => {
  const imageUrl = imageFileComputed.value.url
  const lastUpdated = imageFileComputed.value.lastUpdated
  
  // If URL hasn't changed and we already have the image, don't reload
  if (currentImageUrl.value === imageUrl && (fullImageSrc.value || fullImageFileInIDB.value)) {
    return
  }
  
  // URL changed, reset state
  if (currentImageUrl.value !== imageUrl) {
    if (blobUrlRef.value) {
      const cached = currentImageUrl.value
        ? imageSrcCache.get(currentImageUrl.value)
        : null
      if (!cached || cached.src !== blobUrlRef.value) {
        URL.revokeObjectURL(blobUrlRef.value)
      }
      blobUrlRef.value = null
    }
    fullImageSrc.value = ''
    fullImageFileInIDB.value = undefined
    isFullImageLoaded.value = false
    currentImageUrl.value = imageUrl
  }
  
  if (!imageUrl) {
    handleSetupMissingImage()
    return
  }

  const cached = getCachedImage(imageUrl, lastUpdated)
  if (cached) {
    if (DEBUG_IMAGE_CACHE) {
      console.debug('[BaseImage] cache hit', {
        url: imageUrl,
        lastUpdated,
        isBlob: cached.isBlob,
      })
    }
    fullImageSrc.value = cached.src
    imageRef.value?.classList.remove('anim-bg')
    placeholderRef.value?.classList.remove('anim-bg')
    return
  }
  
  fullImageFileInIDB.value = await getImage(imageUrl)
  if (DEBUG_IMAGE_CACHE) {
    console.debug('[BaseImage] idb lookup', {
      url: imageUrl,
      hit: Boolean(fullImageFileInIDB.value),
      lastUpdated,
    })
  }

  if (!fullImageFileInIDB.value) {
    if (DEBUG_IMAGE_CACHE) {
      console.debug('[BaseImage] idb miss, fetching', { url: imageUrl, lastUpdated })
    }
    void addImage(imageFileComputed.value)
    if (blobUrlRef.value) {
      URL.revokeObjectURL(blobUrlRef.value)
      blobUrlRef.value = null
    }
    fullImageSrc.value = imageUrl
    setCachedImage(imageUrl, {
      src: imageUrl,
      lastUpdated,
      isBlob: false,
    })
    return
  }

  if (fullImageFileInIDB.value) {
    if (
      typeof lastUpdated === 'number' &&
      fullImageFileInIDB.value.lastUpdated !== lastUpdated
    ) {
      if (DEBUG_IMAGE_CACHE) {
        console.debug('[BaseImage] idb stale, updating', {
          url: imageUrl,
          lastUpdated,
          storedLastUpdated: fullImageFileInIDB.value.lastUpdated,
        })
      }
      void updateImage(imageFileComputed.value)
      if (blobUrlRef.value) {
        URL.revokeObjectURL(blobUrlRef.value)
        blobUrlRef.value = null
      }
      fullImageSrc.value = imageUrl
      setCachedImage(imageUrl, {
        src: imageUrl,
        lastUpdated,
        isBlob: false,
      })
      return
    }
    if (blobUrlRef.value) {
      URL.revokeObjectURL(blobUrlRef.value)
      blobUrlRef.value = null
    }
    blobUrlRef.value = URL.createObjectURL(fullImageFileInIDB.value.blob)
    fullImageSrc.value = blobUrlRef.value
    setCachedImage(imageUrl, {
      src: blobUrlRef.value,
      lastUpdated: fullImageFileInIDB.value.lastUpdated,
      isBlob: true,
    })
    if (DEBUG_IMAGE_CACHE) {
      console.debug('[BaseImage] idb hit, using blob', {
        url: imageUrl,
        lastUpdated: fullImageFileInIDB.value.lastUpdated,
      })
    }
  }
}

const loadedFullImage = () => {
  imageRef.value?.classList.remove('anim-bg')
  isFullImageLoaded.value = true
}

watch(isVisible, (newVal) => {
  if (newVal) {
    giveFullImageSourcePlease()
  }
})

// Watch for changes to imageFile.url and reload
watch(() => imageFileComputed.value.url, async (newUrl, oldUrl) => {
  if (newUrl !== oldUrl && isVisible.value) {
    // URL changed and component is visible, reload immediately
    await giveFullImageSourcePlease()
  }
})

// Watch for when image element is rendered and attach load listener
watch(imageRef, (newRef, oldRef) => {
  if (oldRef) {
    oldRef.removeEventListener('load', loadedFullImage)
  }
  if (newRef) {
    newRef.addEventListener('load', loadedFullImage)
  }
})

onMounted(async () => {
  const imageUrl = imageFileComputed.value.url
  const cached = imageUrl
    ? getCachedImage(imageUrl, imageFileComputed.value.lastUpdated)
    : null
  if (cached) {
    fullImageSrc.value = cached.src
  } else {
    placeholderRef.value?.classList.add('anim-bg')
  }

  observer = new IntersectionObserver((entries) => {
    // The callback will be called when the image enters or leaves the viewport
    if (entries[0]?.isIntersecting) {
      // The image has entered the viewport
      isVisible.value = true
      // We don't need the observer anymore, so we disconnect it
      observer?.disconnect()
    }
  }, {
    threshold: 0
  })

  // Start observing the placeholder or image element
  const elementToObserve = placeholderRef.value || imageRef.value
  if (elementToObserve) {
    observer.observe(elementToObserve)
  }
  
  // Watch for when imageRef becomes available and observe it
  watch(imageRef, (newRef) => {
    if (newRef && observer) {
      observer.observe(newRef)
    }
  })
})


onUnmounted(() => {
  // Clean up event listener
  imageRef.value?.removeEventListener('load', loadedFullImage)
  // Clean up IntersectionObserver to prevent memory leaks
  observer?.disconnect()
  observer = null
  if (blobUrlRef.value) {
    const cached = currentImageUrl.value
      ? imageSrcCache.get(currentImageUrl.value)
      : null
    if (!cached || cached.src !== blobUrlRef.value) {
    URL.revokeObjectURL(blobUrlRef.value)
    }
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
  z-index var(--z-index-image-overlay)

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
