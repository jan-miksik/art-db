export type IImageFile = {
  url: string
  lastUpdated?: number
}

export default class ImageFile {
  public url
  public lastUpdated

  constructor(data: IImageFile) {
    this.url = data.url || ''
    this.lastUpdated = data.lastUpdated || new Date('1990').getTime()
  }
}
