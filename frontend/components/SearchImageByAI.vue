<template>
  <div class="search-image-by-ai" ref="menuRef">
    <div class="search-image-by-ai__toggle" @click="handleClickSelectImage">
      <img src="~/assets/search-by-image.png" width="23" height="23" alt="Icon by Adioma"/>
    </div>
    <img v-if="selectedImageInUI" :src="selectedImageInUI" height="250" class="search-image-by-ai__image"/>
    <input type="file" id="file" ref="file" @change="handleSearchImages" style="display: none" accept="image/*" />
    <div v-if="selectedImageInUI" @click="handleRemoveSelectedImage" class="search-image-by-ai__remove-image">X</div>

  </div>
</template>

<script setup lang="ts">
import axios from "axios";
const config = useRuntimeConfig();

const selectedPicture = ref<File | null>()
const searchResults = ref([])
const file = ref();
const filterStore = useFilterStore()

const handleSearchImages = async (event: Event) => {
  const files = (event.target as HTMLInputElement).files
  if (files && files.length > 0) {
    selectedPicture.value = files[0]
  }
  try {
    if(!selectedPicture.value) return
    const formData = new FormData();
    formData.append('image', selectedPicture.value);
    formData.append('limit', "5");
    const response = await axios.post(`${config.public.DJANGO_SERVER_URL}/artists/search-authors-by-image-data/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    const payload = response.data;
    if (!payload?.success) {
      console.error("Search failed:", payload?.error);
      searchResults.value = [];
      selectedPicture.value = undefined;
      if (file.value) {
        file.value.value = '';
      }
      filterStore.filterByIds([]);
      return;
    }
    searchResults.value = payload.data ?? [];
    type SearchResult = { artwork: unknown; author: { id: string } };
    const matchingIds = (searchResults.value as SearchResult[]).map((item) => Number(item.author.id));
    filterStore.filterByIds(matchingIds)
  } catch (error) {
    console.error(error)
  }
}

const handleClickSelectImage = () => {
  file.value.click();
};

const handleRemoveSelectedImage = () => {
  selectedPicture.value = undefined
  if (file.value) {
    file.value.value = '';
  }
}

const selectedImageInUI = ref<string | null>(null)

watchEffect((onCleanup) => {
  if (selectedPicture.value) {
    const url = URL.createObjectURL(selectedPicture.value)
    selectedImageInUI.value = url
    onCleanup(() => URL.revokeObjectURL(url))
  } else {
    selectedImageInUI.value = null
  }
})

</script>

<style lang="stylus" scoped>

.search-image-by-ai
  font-weight: 700;
  font-size: 1.5rem;
  cursor: pointer;
  z-index: var(--z-index-ui-controls);
  font-family: 'Roboto', sans-serif;
  text-align: center;
  background-color: white;


.search-image-by-ai__toggle
  position absolute
  left 0.5rem
  top 0
  cursor pointer

.search-image-by-ai__select-picture
  width: 100px;
  font-size: 1rem
  border 1px solid
  padding 0.2rem

.search-image-by-ai__remove-image
  position absolute
  left 3.5rem
  top 0
  cursor pointer

.search-image-by-ai__image
  object-fit: contain;
  position absolute
  left 0.5rem
  top 2.5rem

.search-image-by-ai__menu
  display: flex;
  flex-direction: column;
  width: 5.2rem;
  gap 0.5rem

</style>
