import { ref } from "vue";
// import useAdminPage from "./useAdminPage";

const isDragging = ref(false);
const isOverPieceOrSetup = ref(false);
const isOverPieceOrSetupInPublicPage = ref(false);
const zIndexOfLastSelectedPiece = ref(1);
const mouseDownPosition = ref<{ x: number; y: number } | null>(null);
const DRAG_THRESHOLD = 5; // pixels of movement to consider it a drag

export default function useMouseActionDetector() {
  // const { isOnAdminPage, isSetupForMobile } = useAdminPage();

  const mouseDownHandler = (event?: MouseEvent) => {
    isDragging.value = false;
    // Track mouse position on mousedown to detect movement
    if (event) {
      mouseDownPosition.value = { x: event.clientX, y: event.clientY };
    } else {
      mouseDownPosition.value = null;
    }
  };

  const mouseMoveHandler = (event?: MouseEvent) => {
    isOverPieceOrSetup.value = true;
    // Only set dragging to true if mouse has moved beyond threshold
    if (event && mouseDownPosition.value) {
      const deltaX = Math.abs(event.clientX - mouseDownPosition.value.x);
      const deltaY = Math.abs(event.clientY - mouseDownPosition.value.y);
      if (deltaX > DRAG_THRESHOLD || deltaY > DRAG_THRESHOLD) {
        isDragging.value = true;
      }
    } else {
      // Fallback: if no position tracking, assume any movement is dragging
      isDragging.value = true;
    }
  };

  const mouseUpHandler = () => {
    mouseDownPosition.value = null;
    setTimeout(() => {
        isDragging.value = false;
    }, 300);
  };

  const mouseLeaveHandler = () => {
    isOverPieceOrSetup.value = false;
    isDragging.value = false;
    mouseDownPosition.value = null;
  };

  const touchmoveHandler = () => {
    // if (!isOnAdminPage.value) return;
    isOverPieceOrSetup.value = true;
  };

  const touchendHandler = () => {
    isOverPieceOrSetup.value = false;
  };

  // Public page
  const mouseMoveHandlerPublicPage = () => {
    isOverPieceOrSetupInPublicPage.value = true;
  };
  const mouseLeaveHandlerPublicPage = () => {
    isOverPieceOrSetupInPublicPage.value = false;
  };

  const touchmoveHandlerPublicPage = () => {
    isOverPieceOrSetupInPublicPage.value = true;
  };

  const touchendHandlerPublicPage = () => {
    isOverPieceOrSetupInPublicPage.value = false;
  };


  return {
    mouseDownHandler,
    mouseMoveHandler,
    mouseUpHandler,
    mouseLeaveHandler,
    touchmoveHandler,
    touchendHandler,
    mouseMoveHandlerPublicPage,
    mouseLeaveHandlerPublicPage,
    touchmoveHandlerPublicPage,
    touchendHandlerPublicPage,
    isOverPieceOrSetupInPublicPage,
    isDragging,
    isOverPieceOrSetup,
    zIndexOfLastSelectedPiece,
  };
}
