/**
 * Composable for implementing focus trap in modals
 * Ensures keyboard navigation stays within the modal when it's open
 */
export const useFocusTrap = (containerRef: Ref<HTMLElement | undefined>) => {
  let previousActiveElement: HTMLElement | null = null
  let firstFocusableElement: HTMLElement | null = null
  let lastFocusableElement: HTMLElement | null = null

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

    if (!firstFocusableElement) {
      firstFocusableElement = focusableElements[0]
    }
    if (!lastFocusableElement) {
      lastFocusableElement = focusableElements[focusableElements.length - 1]
    }

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

    // Store the previously focused element
    previousActiveElement = document.activeElement as HTMLElement

    // Get focusable elements
    const focusableElements = getFocusableElements()
    if (focusableElements.length > 0) {
      firstFocusableElement = focusableElements[0]
      lastFocusableElement = focusableElements[focusableElements.length - 1]
      
      // Focus the first focusable element
      firstFocusableElement.focus()
    }

    // Add event listener for Tab key
    containerRef.value.addEventListener('keydown', trapFocus)
  }

  const deactivate = () => {
    if (!containerRef.value) return

    // Remove event listener
    containerRef.value.removeEventListener('keydown', trapFocus)

    // Restore focus to the previously active element
    if (previousActiveElement) {
      previousActiveElement.focus()
      previousActiveElement = null
    }

    // Reset references
    firstFocusableElement = null
    lastFocusableElement = null
  }

  return {
    activate,
    deactivate,
  }
}
