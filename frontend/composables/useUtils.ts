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
  return Math.floor(Math.random() * (max - min + 1) + min)
}

/**
 * Creates a promise that resolves after the specified number of milliseconds
 * @param ms - Number of milliseconds to wait
 * @returns Promise that resolves after the delay
 */
export const sleep = async (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms))
}
