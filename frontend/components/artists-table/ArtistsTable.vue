<template>
  <div ref="parentRef" class="artists-table__scroll">
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
            :style="{ width: header.column.getSize() ? `${header.column.getSize()}px` : undefined }"
          >
            <FlexRender
              v-if="!header.isPlaceholder"
              :render="header.column.columnDef.header"
              :props="header.getContext()"
            />
          </th>
        </tr>
      </thead>
      <tbody
        class="artists-table__body"
        :style="{ height: `${totalSize}px` }"
      >
        <tr
          v-for="virtualRow in virtualRows"
          :key="getRow(virtualRow.index)?.original.id ?? String(virtualRow.key)"
          :class="[
            'artists-table__row',
            virtualRow.index % 2 === 0 ? 'artists-table__row--even' : 'artists-table__row--odd',
          ]"
          :style="{ transform: `translateY(${virtualRow.start}px)`, height: `${virtualRow.size}px` }"
          @click="getRow(virtualRow.index) && openModal(getRow(virtualRow.index)!.original)"
        >
          <td 
            v-for="cell in getRow(virtualRow.index)?.getVisibleCells?.() ?? []" 
            :key="cell.id"
            :style="{ width: cell.column.getSize() ? `${cell.column.getSize()}px` : undefined }"
          >
            <FlexRender
              :render="cell.column.columnDef.cell"
              :props="cell.getContext()"
            />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="tsx">
import { computed, ref, watch } from 'vue'
import { FlexRender } from '@tanstack/vue-table'
import { useVirtualizer } from '@tanstack/vue-virtual'
import useArtistModal from "./../useArtistModal";
import type { Artist } from '~/J/useArtistsStore'
import { useArtistsTable } from '~/composables/useArtistsTable'

const {openArtistModal} = useArtistModal()
const { table } = useArtistsTable()

const openModal = (artistData: Artist) => {
  openArtistModal(artistData)
}

const rows = computed(() => table.getRowModel().rows)

const parentRef = ref<HTMLElement | null>(null)
const rowVirtualizer = useVirtualizer({
  count: rows.value.length,
  getScrollElement: () => parentRef.value,
  estimateSize: () => 90,
  overscan: 10,
})

watch(rows, () => {
  rowVirtualizer.value.setOptions({
    ...rowVirtualizer.value.options,
    count: rows.value.length,
  })
  rowVirtualizer.value.measure()
})

const virtualRows = computed(() =>
  rowVirtualizer.value.getVirtualItems().filter((v) => v.index >= 0 && v.index < rows.value.length)
)
const totalSize = computed(() => rowVirtualizer.value.getTotalSize())

const getRow = (index: number) => {
  const row = rows.value[index]
  return row ?? null
}
</script>

<style lang="stylus">
.artists-table
  position relative
  top 200px
  margin: auto
  max-width: 55rem
  margin-bottom 30rem
  border-spacing 0
  table-layout: fixed

.artists-table thead
  display: table
  width: 100%
  table-layout: fixed

.artists-table__scroll
  max-height: 100vh
  overflow: auto
  width: 100%

.artists-table__body
  position: relative
  display: block
  width: 100%

.artists-table__row
  position: absolute
  left: 0
  width: 100%
  display: table
  table-layout: fixed

.artists-table__row--even
  background-color: #f0f0f0

.artists-table__row--odd
  background-color: transparent

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

</style>
