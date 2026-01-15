import type { Ref } from 'vue'

/**
 * Composable for implementing focus trap in modals
 * Ensures keyboard navigation stays within the modal when it's open
 */
export const useFocusTrap = (containerRef: Ref<HTMLElement | undefined>) => {
  let previousActiveElement: HTMLElement | null = null
  let firstFocusableElement: HTMLElement | null = null
  let lastFocusableElement: HTMLElement | null = null
  let activatedElement: HTMLElement | null = null

  const getFocusableElements = (): HTMLElement[] => {
    if (!containerRef.value) return []

    const focusableSelectors = [
      'a[href]',
      'button:not([disabled])',
      'textarea:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      '[tabindex]:not([tabindex="-1"])',
    ].join(', ')

    return Array.from(
      containerRef.value.querySelectorAll<HTMLElement>(focusableSelectors)
    ).filter((el) => {
      const style = window.getComputedStyle(el)
      return !el.hasAttribute('disabled') && 
             el.getAttribute('aria-hidden') !== 'true' &&
             style.visibility !== 'hidden' &&
             style.display !== 'none'
    })
  }

  const trapFocus = (e: KeyboardEvent) => {
    if (e.key !== 'Tab') return

    const focusableElements = getFocusableElements()
    if (focusableElements.length === 0) return

    // Always get fresh references to reflect current DOM
    firstFocusableElement = focusableElements[0]
    lastFocusableElement = focusableElements[focusableElements.length - 1]

    if (e.shiftKey) {
      // Shift + Tab
      if (document.activeElement === firstFocusableElement) {
        e.preventDefault()
        lastFocusableElement?.focus()
      }
    } else {
      // Tab
      if (document.activeElement === lastFocusableElement) {
        e.preventDefault()
        firstFocusableElement?.focus()
      }
    }
  }

  const activate = () => {
    if (!containerRef.value) return

    previousActiveElement = document.activeElement as HTMLElement

    activatedElement = containerRef.value

    const focusableElements = getFocusableElements()
    if (focusableElements.length > 0) {
      firstFocusableElement = focusableElements[0]
      lastFocusableElement = focusableElements[focusableElements.length - 1]
      firstFocusableElement.focus()
    }

    activatedElement.addEventListener('keydown', trapFocus)
  }

  const deactivate = () => {
    if (activatedElement) {
      activatedElement.removeEventListener('keydown', trapFocus)
      activatedElement = null
    }

    if (previousActiveElement) {
      previousActiveElement.focus()
      previousActiveElement = null
    }

    firstFocusableElement = null
    lastFocusableElement = null
  }

  return {
    activate,
    deactivate,
  }
}
