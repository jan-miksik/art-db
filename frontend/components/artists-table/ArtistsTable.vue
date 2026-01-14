<template>
  <table class="artists-table">
    <thead>
      <tr
        v-for="headerGroup in table.getHeaderGroups()"
        :key="headerGroup.id"
      >
        <th
          v-for="header in headerGroup.headers"
          :key="header.id"
          :colSpan="header.colSpan"
        >
          <FlexRender
            v-if="!header.isPlaceholder"
            :render="header.column.columnDef.header"
            :props="header.getContext()"
          />
        </th>
      </tr>
    </thead>
    <TransitionGroup
      name="list"
      tag="tbody"
      :css="false"
      @before-enter="onBeforeEnter"
      @enter="onEnter"
      @leave="onLeave"
    >
      <tr
        v-for="(row, index) in table.getRowModel().rows"
        :key="row.original.id"
        :data-index="index"
        @click="openModal(row.original)"
      >
        <td v-for="cell in row.getVisibleCells()" :key="cell.id">
          <FlexRender
            :render="cell.column.columnDef.cell"
            :props="cell.getContext()"
          />
        </td>
      </tr>
    </TransitionGroup>
  </table>
</template>

<script setup lang="tsx">
import {computed} from 'vue'
import {useFilterStore} from '~/J/useFilterStore'
import {useSortStore} from '~/J/useSortStore'
import {
  FlexRender,
  getCoreRowModel,
  useVueTable,
  createColumnHelper,
} from '@tanstack/vue-table'
import BaseImage from "~/components/BaseImage.vue";
import useArtistModal from "./../useArtistModal";
import gsap from 'gsap'

const {openArtistModal} = useArtistModal()

const openModal = (artistData: any) => {
  openArtistModal(artistData)
}

const columnHelper = createColumnHelper<Artist>()

const columns = [
  columnHelper.accessor('profile_image_url', {
    header: () => '',
    cell: props => {
      return h(BaseImage, {
        imageFile: {
          url: props.row.original.profile_image_url,
          lastUpdated: props.row.original.artworks[0].year
        },
        externalCssClass: ['artist-table__profile-image'],
        key: props.row.original.id
      });
    },
  }),
  columnHelper.accessor('name', {
    cell: info => info.getValue(),
    header: () => '',
  }),
  columnHelper.accessor('artworks', {
    header: () => '',
    cell: props => {
      return (
          <div class="artist-table__artworks-preview" key={`${props.row.original.id}-artworks`}>
            {props.row.original.artworks.map((artwork, index) => (
                <BaseImage
                    key={`${props.row.original.id}-artwork`}
                    imageFile={{
                      url: artwork.picture_url,
                      lastUpdated: artwork.year
                    }}
                    externalCssClass={['artist-table__artwork-preview-image']}
                />
            ))}
          </div>
      );
    },
  }),
]

const artistsStore = useArtistsStore()
const sortStore = useSortStore()

// Animation functions
const onBeforeEnter = (el: Element) => {
  const element = el as HTMLElement
  element.style.opacity = '0'
  element.style.transform = 'translateY(30px)'
}

const onEnter = (el: Element, done: () => void) => {
  const element = el as HTMLElement
  const delay = element.dataset.index ? parseInt(element.dataset.index) * 0.1 : 0

  gsap.to(element, {
    opacity: 1,
    y: 0,
    duration: 0.6,
    delay,
    ease: 'power2.out',
    onComplete: done
  })
}

const onLeave = (el: Element, done: () => void) => {
  const element = el as HTMLElement
  gsap.to(element, {
    opacity: 0,
    y: 30,
    duration: 0.6,
    ease: 'power2.in',
    onComplete: done
  })
}

// Create a reactive data source
const data = computed(() => {
  return [...artistsStore.artists]
})

// Create the table with computed data
const table = useVueTable({
  get data() {
    return data.value
  },
  columns,
  getCoreRowModel: getCoreRowModel(),
})
</script>

<style lang="stylus">
.artists-table
  position relative
  top 200px
  margin: auto
  width: 90%
  margin-bottom 30rem
  border-spacing 0

.artists-table tr:nth-child(2n)
  background-color: #f0f0f0;

.artists-table tr:hover
  background: linear-gradient(46deg, #c7c7cc, rgba(177, 184, 182, 0.56), #4d503f3d);
  cursor pointer

.artist-table__profile-image
  width 70px
  height 70px
  object-fit cover
  object-position center
  filter: grayscale(1);
  cursor default

th
  text-align: left;
  opacity: 0.6;

.artist-table__artworks-preview
  display flex
  gap 1rem

.artist-table__artwork-preview-image
  height 70px
  object-fit contain
  object-position center
  cursor default

// Animation classes
.list-move,
.list-enter-active,
.list-leave-active
  transition: all 0.6s ease

.list-leave-active
  position: absolute
  width: 100%

.list-enter-from
  opacity: 0
  transform: translateY(30px)

.list-leave-to
  opacity: 0
  transform: translateY(-30px)
</style>
