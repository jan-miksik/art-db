import useMouseActionDetector from "~/J/useMouseActionDetector";
import type { Artist } from "./Artist.vue";

const isOpen = ref(false);
const artistData = ref<Artist>();

export default function useArtistModal() {
  const { isDragging } = useMouseActionDetector();

  const openArtistModal = (artistDataToSet: Artist) => {
    if (!isDragging.value) {
      isOpen.value = true;
      artistData.value = artistDataToSet;
    }
  };
  return {
    isOpen,
    artistData,
    openArtistModal
  }
}