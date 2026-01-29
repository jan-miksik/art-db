<template>
  <teleport v-if="isOpen && artistData" to="body">
    <div
      ref="modalRef"
      class="artist-modal"
      @click="handleBackgroundClick"
      @keydown="handleKeydown"
      tabindex="0"
    >
      <!-- Close button -->
      <button class="artist-modal__close" @click="closeModal" aria-label="Close gallery">
        <svg width="24" height="24" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="m 4.5455939,2.5001916 c -0.1744558,0 -0.3491034,0.066454 -0.4820544,0.1997463 L 2.6999379,4.0635395 c -0.2665841,0.2665841 -0.2665841,0.6982065 0,0.9641088 L 7.6722899,10 2.6999379,14.972352 c -0.2665841,0.266584 -0.2665841,0.698206 0,0.964108 l 1.3636016,1.363602 c 0.2665841,0.266584 0.6982065,0.266584 0.9641088,0 L 10,12.32771 l 4.972352,4.972352 c 0.265902,0.266584 0.698206,0.266584 0.964108,0 l 1.363602,-1.363602 c 0.266584,-0.266584 0.266584,-0.698206 0,-0.964108 L 12.32771,10 17.300062,5.0276483 c 0.266584,-0.2659023 0.266584,-0.6982065 0,-0.9641088 L 15.93646,2.6999379 c -0.266584,-0.2665841 -0.698206,-0.2665841 -0.964108,0 L 10,7.6722899 5.0276483,2.6999379 C 4.8943562,2.5666458 4.7200496,2.5001916 4.5455939,2.5001916 Z" stroke="currentColor" stroke-width="0.5" fill="currentColor"/>
        </svg>
      </button>

      <!-- Artist header -->
      <header class="artist-modal__header" @click.stop>
        <BaseImage
          :image-file="{ url: artistData.profile_image_url ?? '' }"
          :external-css-class="['artist-modal__profile-image']"
          :alt="`Profile image of ${artistData.name}`"
        />
        <h2 class="artist-modal__name">{{ artistData.name }}</h2>
      </header>

      <!-- Gallery grid view (when no artwork selected) -->
      <div
        v-if="selectedIndex === null"
        class="artist-modal__gallery"
        @click.stop
        role="grid"
        :aria-label="`Artwork gallery for ${artistData.name}`"
      >
        <button
          v-for="(piece, index) in artistData.artworks"
          :key="piece.id || index"
          class="artist-modal__grid-item"
          :style="{ '--delay': `${index * 60}ms` }"
          @click="selectArtwork(index)"
          :aria-label="`View ${piece.title || 'Untitled'}${piece.year ? `, ${piece.year}` : ''}`"
        >
          <div class="artist-modal__grid-item-inner">
            <BaseImage
              :image-file="{ url: piece.picture_url ?? '' }"
              :external-css-class="['artist-modal__grid-image']"
              :alt="`${piece.title || 'Untitled artwork'} by ${artistData.name}`"
            />
            <div class="artist-modal__grid-overlay">
              <span class="artist-modal__grid-title">{{ piece.title || 'Untitled' }}</span>
              <span v-if="piece.year" class="artist-modal__grid-year">{{ piece.year }}</span>
            </div>
          </div>
        </button>
      </div>

      <!-- Full-screen artwork view (when artwork selected) -->
      <div
        v-else
        class="artist-modal__lightbox"
        @click="closeLightbox"
      >
        <!-- Close button for lightbox -->
        <button class="artist-modal__close artist-modal__close--lightbox" @click.stop="closeLightbox" aria-label="Close artwork view">
          <svg width="24" height="24" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="m 4.5455939,2.5001916 c -0.1744558,0 -0.3491034,0.066454 -0.4820544,0.1997463 L 2.6999379,4.0635395 c -0.2665841,0.2665841 -0.2665841,0.6982065 0,0.9641088 L 7.6722899,10 2.6999379,14.972352 c -0.2665841,0.266584 -0.2665841,0.698206 0,0.964108 l 1.3636016,1.363602 c 0.2665841,0.266584 0.6982065,0.266584 0.9641088,0 L 10,12.32771 l 4.972352,4.972352 c 0.265902,0.266584 0.698206,0.266584 0.964108,0 l 1.363602,-1.363602 c 0.266584,-0.266584 0.266584,-0.698206 0,-0.964108 L 12.32771,10 17.300062,5.0276483 c 0.266584,-0.2659023 0.266584,-0.6982065 0,-0.9641088 L 15.93646,2.6999379 c -0.266584,-0.2665841 -0.698206,-0.2665841 -0.964108,0 L 10,7.6722899 5.0276483,2.6999379 C 4.8943562,2.5666458 4.7200496,2.5001916 4.5455939,2.5001916 Z" stroke="currentColor" stroke-width="0.5" fill="currentColor"/>
          </svg>
        </button>

        <div class="artist-modal__lightbox-content" @click.stop>
          <!-- Navigation arrows -->
          <button
            v-if="artistData.artworks.length > 1"
            class="artist-modal__nav artist-modal__nav--prev"
            @click="navigateArtwork(-1)"
            :disabled="selectedIndex === 0"
            aria-label="Previous artwork"
            type="button"
          >
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
              <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="1.5"/>
            </svg>
          </button>

          <!-- Main artwork display -->
          <div class="artist-modal__artwork-container" @click.stop>
            <Transition 
              :name="navigationDirection === 'next' ? 'artwork-slide-next' : navigationDirection === 'prev' ? 'artwork-slide-prev' : 'artwork-fade'" 
              mode="out-in"
            >
              <BaseImage
                :key="`artwork-${selectedIndex}-${selectedArtwork?.picture_url}`"
                :image-file="{ url: selectedArtwork?.picture_url ?? '' }"
                :external-css-class="['artist-modal__lightbox-image']"
                :alt="`${selectedArtwork?.title || 'Untitled'} by ${artistData.name}`"
              />
            </Transition>
            <div class="artist-modal__artwork-info">
              <h3 class="artist-modal__artwork-title">{{ selectedArtwork?.title || 'Untitled' }}</h3>
              <p v-if="selectedArtwork?.year" class="artist-modal__artwork-year">{{ selectedArtwork.year }}</p>
            </div>
          </div>

          <button
            v-if="artistData.artworks.length > 1"
            class="artist-modal__nav artist-modal__nav--next"
            @click="navigateArtwork(1)"
            :disabled="selectedIndex === artistData.artworks.length - 1"
            aria-label="Next artwork"
            type="button"
          >
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
              <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="1.5"/>
            </svg>
          </button>
        </div>

        <!-- Thumbnail strip -->
        <div v-if="artistData.artworks.length > 1" class="artist-modal__thumbnails" @click.stop>
          <button
            v-for="(piece, index) in artistData.artworks"
            :key="`thumb-${piece.id || index}`"
            class="artist-modal__thumbnail"
            :class="{ 'artist-modal__thumbnail--active': index === selectedIndex }"
            @click="selectArtwork(index)"
            :aria-label="`Go to artwork ${index + 1}: ${piece.title || 'Untitled'}`"
          >
            <BaseImage
              :image-file="{ url: piece.picture_url ?? '' }"
              :external-css-class="['artist-modal__thumbnail-image']"
              :alt="`Thumbnail of ${piece.title || 'Untitled'}`"
            />
          </button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import useArtistModal from "./useArtistModal";

const { isOpen, artistData } = useArtistModal();

const modalRef = ref<HTMLElement>()
const { activate: activateFocusTrap, deactivate: deactivateFocusTrap } = useFocusTrap(modalRef)

// Gallery state
const selectedIndex = ref<number | null>(null)
const navigationDirection = ref<'next' | 'prev' | null>(null)

const selectedArtwork = computed(() => {
  if (selectedIndex.value === null || !artistData.value) return null
  return artistData.value.artworks[selectedIndex.value]
})

const closeModal = () => {
  selectedIndex.value = null
  isOpen.value = false
}

const handleBackgroundClick = (e: MouseEvent) => {
  if (e.target === e.currentTarget) {
    closeModal()
  }
}

const selectArtwork = (index: number) => {
  if (selectedIndex.value !== null && index > selectedIndex.value) {
    navigationDirection.value = 'next'
  } else if (selectedIndex.value !== null && index < selectedIndex.value) {
    navigationDirection.value = 'prev'
  }
  selectedIndex.value = index
}

const closeLightbox = () => {
  selectedIndex.value = null
  navigationDirection.value = null
}

const navigateArtwork = (direction: number) => {
  if (selectedIndex.value === null || !artistData.value || !artistData.value.artworks) return
  const currentIndex = selectedIndex.value
  const newIndex = currentIndex + direction
  if (newIndex >= 0 && newIndex < artistData.value.artworks.length) {
    navigationDirection.value = direction > 0 ? 'next' : 'prev'
    selectedIndex.value = newIndex
  }
}

const handleKeydown = (e: KeyboardEvent) => {
  if (!isOpen.value) return
  
  if (e.key === 'Escape') {
    if (selectedIndex.value !== null) {
      closeLightbox()
    } else {
      closeModal()
    }
  } else if (selectedIndex.value !== null) {
    if (e.key === 'ArrowLeft') {
      e.preventDefault()
      navigateArtwork(-1)
    } else if (e.key === 'ArrowRight') {
      e.preventDefault()
      navigateArtwork(1)
    }
  }
}

// Global keyboard listener that works regardless of focus
onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  deactivateFocusTrap()
})

watch([isOpen, () => artistData.value, modalRef], ([newIsOpen, , newRef]) => {
  if (newIsOpen && artistData.value && newRef) {
    nextTick(() => {
      if (isOpen.value && modalRef.value) {
        activateFocusTrap()
        modalRef.value.focus()
      }
    })
  } else {
    deactivateFocusTrap()
  }
})

// Reset selected index when modal closes
watch(isOpen, (newIsOpen) => {
  if (!newIsOpen) {
    selectedIndex.value = null
  }
})

</script>

<style lang="stylus" scoped>
// ═══════════════════════════════════════════════════════════════
// EDITORIAL MUSEUM GALLERY
// A refined, catalog-inspired artwork viewing experience
// ═══════════════════════════════════════════════════════════════

// Noise texture for film-grain effect
noise-texture()
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")
  background-size: 150px

// ─────────────────────────────────────────────────────────────────
// BASE MODAL
// ─────────────────────────────────────────────────────────────────
.artist-modal
  position: fixed
  inset: 0
  background: #f5f5f3
  z-index: var(--z-index-modal)
  display: flex
  flex-direction: column
  overflow: hidden
  outline: none
  // Subtle paper texture
  &::before
    content: ''
    position: absolute
    inset: 0
    noise-texture()
    opacity: 0.03
    pointer-events: none

// ─────────────────────────────────────────────────────────────────
// CLOSE BUTTON
// ─────────────────────────────────────────────────────────────────
.artist-modal__close
  position: fixed
  top: 0
  right: 0
  z-index: 100
  width: 80px
  height: 80px
  display: flex
  align-items: center
  justify-content: center
  background: transparent
  border: none
  color: #1a1a1a
  cursor: url('~/assets/close.svg'), pointer
  transition: all 0.2s ease
  padding: 0
  &:hover
    color: #666
  &:focus-visible
    outline: 2px solid #1a1a1a
    outline-offset: 2px
  svg
    width: 24px
    height: 24px
  &--lightbox
    color: #fff
    cursor: url('~/assets/close-white.svg'), pointer
    &:hover
      color: rgba(255,255,255,0.7)
    &:focus-visible
      outline-color: #fff

// ─────────────────────────────────────────────────────────────────
// HEADER
// ─────────────────────────────────────────────────────────────────
.artist-modal__header
  position: fixed
  top: 1.5rem
  left: 1.5rem
  display: flex
  align-items: center
  gap: 1rem
  cursor: default

.artist-modal__profile-image
  width: 80px
  height: 80px
  border-radius: 50%
  object-fit: cover
  filter: grayscale(1)
  cursor: default

.artist-modal__name
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif
  font-size: 0.875rem
  font-weight: 500
  letter-spacing: 0.05em
  text-transform: uppercase
  color: #fff
  background: #141414
  margin: 0
  padding: 0.15rem 0.5rem
  cursor: default

// ─────────────────────────────────────────────────────────────────
// GALLERY GRID
// ─────────────────────────────────────────────────────────────────
.artist-modal__gallery
  flex: 1
  display: grid
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))
  gap: 2rem
  padding: 15rem 10vw 3rem
  overflow-y: auto
  align-content: start
  justify-content: center
  cursor: default
  // Scrollbar styling
  &::-webkit-scrollbar
    width: 6px
  &::-webkit-scrollbar-track
    background: transparent
  &::-webkit-scrollbar-thumb
    background: #ccc
    border-radius: 3px
    &:hover
      background: #999

.artist-modal__grid-item
  background: none
  border: none
  padding: 0
  cursor: pointer
  // Staggered entrance animation
  animation: gridItemReveal 0.5s ease forwards
  animation-delay: var(--delay)
  opacity: 0
  transform: translateY(20px)
  &:focus-visible
    outline: 2px solid #1a1a1a
    outline-offset: 4px

@keyframes gridItemReveal
  to
    opacity: 1
    transform: translateY(0)

.artist-modal__grid-item-inner
  position: relative
  aspect-ratio: 4 / 5
  overflow: hidden
  background: #e8e8e6
  &::before
    content: ''
    position: absolute
    inset: 0
    noise-texture()
    opacity: 0
    z-index: 2
    pointer-events: none
    transition: opacity 0.3s ease
  &:hover::before
    opacity: 0.05
  &::after
    content: ''
    position: absolute
    inset: 0
    border: 1px solid transparent
    transition: border-color 0.3s ease
    pointer-events: none
  &:hover::after
    border-color: #1a1a1a

.artist-modal__grid-image
  width: 100%
  height: 100%
  object-fit: contain

.artist-modal__grid-overlay
  position: absolute
  bottom: 0
  left: 0
  right: 0
  padding: 1.5rem 1rem 1rem
  background: black
  display: flex
  flex-direction: column
  gap: 0.25rem
  opacity: 0
  transform: translateY(8px)
  transition: all 0.3s ease
  .artist-modal__grid-item:hover &
    opacity: 1
    transform: translateY(0)

.artist-modal__grid-title
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif
  font-size: 0.875rem
  font-weight: 400
  color: #fff
  letter-spacing: 0.02em

.artist-modal__grid-year
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif
  font-size: 0.75rem
  font-weight: 300
  color: rgba(255,255,255,0.7)

// ─────────────────────────────────────────────────────────────────
// LIGHTBOX (FULL-SCREEN VIEW)
// ─────────────────────────────────────────────────────────────────
.artist-modal__lightbox
  position: absolute
  inset: 0
  background: rgba(20, 20, 20, 0.97)
  display: flex
  flex-direction: column
  animation: lightboxFadeIn 0.3s ease

@keyframes lightboxFadeIn
  from
    opacity: 0
  to
    opacity: 1

.artist-modal__lightbox-content
  flex: 1
  display: flex
  align-items: center
  justify-content: center
  padding: 2rem
  gap: 1rem
  cursor: default
  position: relative

.artist-modal__artwork-container
  display: flex
  flex-direction: column
  align-items: center
  gap: 1.5rem
  max-width: 90vw
  max-height: 85vh
  pointer-events: none
  perspective: 1200px
  & > *
    pointer-events: auto

.artist-modal__lightbox-image
  max-width: 90vw
  max-height: 80vh
  width: auto
  height: auto
  object-fit: contain
  box-shadow: 0 20px 60px rgba(0,0,0,0.5)
  transition: opacity 0.4s ease, transform 0.4s ease
  animation: artworkFadeIn 0.5s ease forwards
  opacity: 0
  transform: scale(0.95)

@keyframes artworkFadeIn
  from
    opacity: 0
    transform: scale(0.95)
  to
    opacity: 1
    transform: scale(1)

.artist-modal__artwork-info
  text-align: center

.artist-modal__artwork-title
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif
  font-size: 1.125rem
  font-weight: 400
  color: #fff
  margin: 0
  letter-spacing: 0.02em

.artist-modal__artwork-year
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif
  font-size: 0.875rem
  font-weight: 300
  color: rgba(255,255,255,0.6)
  margin: 0.375rem 0 0

// ─────────────────────────────────────────────────────────────────
// NAVIGATION ARROWS
// ─────────────────────────────────────────────────────────────────
.artist-modal__nav
  position: absolute
  top: 50%
  transform: translateY(-50%)
  width: 56px
  height: 56px
  display: flex
  align-items: center
  justify-content: center
  background: transparent
  border: 1px solid rgba(255,255,255,0.2)
  color: #fff
  cursor: pointer
  transition: all 0.2s ease
  z-index: 10
  pointer-events: auto
  &--prev
    left: 2rem
  &--next
    right: 2rem
  &:hover:not(:disabled)
    border-color: #fff
    background: rgba(255,255,255,0.05)
  &:disabled
    opacity: 0.3
    cursor: not-allowed
    pointer-events: none
  &:focus-visible
    outline: 2px solid #fff
    outline-offset: 2px

// ─────────────────────────────────────────────────────────────────
// THUMBNAIL STRIP
// ─────────────────────────────────────────────────────────────────
.artist-modal__thumbnails
  display: flex
  justify-content: center
  align-items: center
  gap: 0.5rem
  padding: 1rem
  background: rgba(0,0,0,0.3)
  overflow-x: auto
  overflow-y: hidden
  cursor: default
  scrollbar-width: none
  -ms-overflow-style: none
  max-height: 100px
  &::-webkit-scrollbar
    display: none

.artist-modal__thumbnail
  flex-shrink: 0
  width: 56px
  height: 56px
  padding: 0
  background: none
  border: 2px solid transparent
  cursor: pointer
  opacity: 0.5
  transition: all 0.2s ease
  overflow: hidden
  &:hover
    opacity: 0.8
  &--active
    opacity: 1
    border-color: #fff

.artist-modal__thumbnail-image
  width: 100%
  height: 100%
  object-fit: cover

// ─────────────────────────────────────────────────────────────────
// RESPONSIVE ADJUSTMENTS
// ─────────────────────────────────────────────────────────────────
@media (max-width: 768px)
  .artist-modal__gallery
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr))
    gap: 0.75rem
    padding: 5.5rem 0.75rem 1rem

  .artist-modal__header
    top: 0.75rem
    left: 0.75rem

  .artist-modal__close
    top: 0
    right: 0
    width: 60px
    height: 60px

  .artist-modal__profile-image
    width: 48px
    height: 48px

  .artist-modal__name
    font-size: 0.7rem

  .artist-modal__nav
    width: 40px
    height: 40px
    &--prev
      left: 1rem
    &--next
      right: 1rem

  .artist-modal__thumbnail
    width: 44px
    height: 44px

  .artist-modal__lightbox-content
    padding: 1rem

  .artist-modal__thumbnails
    padding: 0.75rem
    gap: 0.375rem
    max-height: 80px

  .artist-modal__thumbnail
    width: 44px
    height: 44px

  .artist-modal__lightbox-image
    max-width: 95vw
    max-height: 85vh

// ─────────────────────────────────────────────────────────────────
// TRANSITION ANIMATIONS - Cross-fade with rotation
// ─────────────────────────────────────────────────────────────────
.artwork-fade-enter-active,
.artwork-slide-next-enter-active,
.artwork-slide-prev-enter-active
  transition: opacity 0.6s cubic-bezier(0.4, 0, 0.2, 1), transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)

.artwork-fade-leave-active,
.artwork-slide-next-leave-active,
.artwork-slide-prev-leave-active
  transition: opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1), transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)

// Fade transition (initial load) - simple cross-fade
.artwork-fade-enter-from
  opacity: 0
  transform: scale(0.98)

.artwork-fade-leave-to
  opacity: 0
  transform: scale(1.02)

// Slide next (going forward) - rotate and slide from right
.artwork-slide-next-enter-from
  opacity: 0
  transform: translateX(80px) rotateY(15deg) scale(0.95)

.artwork-slide-next-leave-to
  opacity: 0
  transform: translateX(-80px) rotateY(-15deg) scale(0.95)

// Slide prev (going backward) - rotate and slide from left
.artwork-slide-prev-enter-from
  opacity: 0
  transform: translateX(-80px) rotateY(-15deg) scale(0.95)

.artwork-slide-prev-leave-to
  opacity: 0
  transform: translateX(80px) rotateY(15deg) scale(0.95)

</style>
