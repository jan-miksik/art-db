import { type IImageFile } from '~/models/ImageFile'
import Dexie, { type Table } from 'dexie'

export interface ImageIDB {
  id: string;
  lastUpdated: number;
  blob: Blob;
}

export default class MySubClassedDexie extends Dexie {
// export default class MySubClassedDexie {
  // 'Images' is added by dexie when declaring the stores()
  // We just tell the typing system this is the case
  images!: Table<ImageIDB>

  constructor() {
    super('imagesDb')
    this.version(1).stores({
      images: 'id, blob, lastUpdated'
    })
  }
}

const DEBUG_IMAGE_CACHE =
  import.meta.env?.DEV === true ||
  (typeof window !== 'undefined' && window.localStorage?.getItem('debug-images') === '1')

const inFlightBlobRequests = new Map<string, Promise<Blob>>()

const getBlobFromUrl = async (imageUrl: string): Promise<Blob> => {
  const existingRequest = inFlightBlobRequests.get(imageUrl)
  if (existingRequest) {
    if (DEBUG_IMAGE_CACHE) {
      console.debug('[idb] fetch blob deduped', { url: imageUrl })
    }
    return existingRequest
  }

  const request = (async () => {
    if (DEBUG_IMAGE_CACHE) {
      console.debug('[idb] fetch blob', { url: imageUrl })
    }
    const res = await fetch(imageUrl)
    return await res.blob()
  })()

  inFlightBlobRequests.set(imageUrl, request)
  try {
    return await request
  } finally {
    inFlightBlobRequests.delete(imageUrl)
  }
}

export const addImage = async (image: IImageFile) => {
  const { url, lastUpdated = Date.now() } = image
  const blob = await getBlobFromUrl(url)

  try {
    await db.images.put({
      id: url,
      blob,
      lastUpdated
    })
    if (DEBUG_IMAGE_CACHE) {
      console.debug('[idb] add image', { url, lastUpdated })
    }
  } catch (error) {
    console.error('addImage error: ', error)
  }
}

export const updateImage = async (image: IImageFile) => {
  const { url, lastUpdated = Date.now() } = image

  const blob = await getBlobFromUrl(url)

  try {
    await db.images.update(url, {
      id: url,
      blob,
      lastUpdated
    })
    if (DEBUG_IMAGE_CACHE) {
      console.debug('[idb] update image', { url, lastUpdated })
    }
  } catch (error) {
    console.error('updateImage error: ', error)
  }
}

export const getImage = async (id: string) => {
  try {
    const imageObj = await db.images.where('id')
      .equals(id).toArray()

    if (DEBUG_IMAGE_CACHE) {
      console.debug('[idb] get image', { id, hit: Boolean(imageObj[0]) })
    }
    return imageObj[0]
  } catch (error) {
    return undefined
  }
}

export const db = new MySubClassedDexie()
