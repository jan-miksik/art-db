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
    <tbody>
      <tr v-for="row in table.getRowModel().rows" :key="row.id" @click="openModal(row.original)">
        <td v-for="cell in row.getVisibleCells()" :key="cell.id">
          <FlexRender
            :render="cell.column.columnDef.cell"
            :props="cell.getContext()"
          />
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="tsx">
const filterStore = useFilterStore()
import {
  FlexRender,
  getCoreRowModel,
  useVueTable,
  createColumnHelper,
} from '@tanstack/vue-table'
import BaseImage from "~/components/BaseImage.vue";
import useArtistModal from "./../useArtistModal";
const { openArtistModal } = useArtistModal()

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

const data = computed(() => useArtistsStore().artists)

const table = useVueTable({
  get data() {
    return data.value
  },
  columns,
  getCoreRowModel: getCoreRowModel(),
})

watch(() => useArtistsStore().artists, () => {
  console.log('useArtistsStore().artists', useArtistsStore().artists)
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
  //border-radius 50%
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
  //width 70px
  height 70px
  //border-radius 50%
  object-fit contain
  object-position center
  //filter: grayscale(1);
  cursor default



</style>
