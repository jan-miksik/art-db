<template>
  <div class="artists-table__scroll">
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
            :style="{
              width: header.column.getSize() ? `${header.column.getSize()}px` : undefined,
              paddingLeft: header.column.id === 'name' ? '1rem' : undefined,
            }"
          >
            <FlexRender
              v-if="!header.isPlaceholder"
              :render="header.column.columnDef.header"
              :props="header.getContext()"
            />
          </th>
        </tr>
      </thead>
      <tbody class="artists-table__body">
        <tr
          v-for="(row, rowIndex) in rows"
          :key="row.id"
          :class="[
            'artists-table__row',
            rowIndex % 2 === 0 ? 'artists-table__row--even' : 'artists-table__row--odd',
          ]"
          @click="openModal(row.original)"
        >
          <td
            v-for="cell in row.getVisibleCells()"
            :key="cell.id"
            :style="{
              width: cell.column.getSize() ? `${cell.column.getSize()}px` : undefined,
              paddingLeft: cell.column.id === 'name' ? '1rem' : undefined,
            }"
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
import { computed } from 'vue'
import { FlexRender } from '@tanstack/vue-table'
import useArtistModal from "./../useArtistModal";
import type { Artist } from '~/J/useArtistsStore'
import { useArtistsTable } from '~/J/useArtistsTable'

const {openArtistModal} = useArtistModal()
const { table } = useArtistsTable()

const openModal = (artistData: Artist) => {
  openArtistModal(artistData)
}

const rows = computed(() => table.getRowModel().rows)
</script>

<style lang="stylus">
.artists-table
  position relative
  top 200px
  margin: auto
  width: 100%
  margin-bottom 30rem
  border-spacing 0
  table-layout: fixed

  @media screen and (min-width: 1024px) {
    width: 55rem
  }

.artists-table__scroll
  overflow: auto
  width: 100%

.artists-table__body

.artists-table__row--even
  background-color: #f0f0f0

.artists-table__row--odd
  background-color: #fff

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
