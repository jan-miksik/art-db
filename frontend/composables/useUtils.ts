/**
 * Utility functions for common operations
 */

/**
 * Generates a random integer between min and max (inclusive)
 * @param min - Minimum value (inclusive)
 * @param max - Maximum value (inclusive)
 * @returns Random integer between min and max
 */
export const randomRange = (min: number, max: number): number => {
  if (!Number.isFinite(min) || !Number.isFinite(max)) {
    throw new TypeError('min and max must be finite numbers')
  }
  const lo = Math.ceil(Math.min(min, max))
  const hi = Math.floor(Math.max(min, max))
  if (lo > hi) {
    throw new RangeError('No integers exist in the given range')
  }
  return Math.floor(Math.random() * (hi - lo + 1)) + lo
}

/**
 * Creates a promise that resolves after the specified number of milliseconds
 * @param ms - Number of milliseconds to wait
 * @returns Promise that resolves after the delay
 */
export const sleep = async (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms))
}
