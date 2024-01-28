<template>
  <div>
    <h1>table of artists</h1>
    <div>
    <table>
      <thead>
        <tr>
          <th>[][][][][][][]</th>
          <th>Name</th>
          <th>Notes</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="artist in artists" :key="artist.id">
          <td class="image-profile">
            <img :src="artist.profile_image" :alt="artist.name" />
          </td>
          <td>{{ artist.name }}</td>
          <td>{{ artist.notes }}</td>
        </tr>
      </tbody>
    </table>
  </div>
  </div>
</template>

<script setup lang="ts">
// import { ref, onMounted } from 'vue';
import axios from 'axios';

const artists = ref<any>([]);

onMounted(async () => {
  console.log('onMounted: ');
  // const response = await axios.get('http://localhost:8000/api/items');
  // let data;

  axios.get('http://localhost:8000/artists/')
    .then(response => {
      console.log('response: ', response);
      console.log('response.data: ', response.data);
      artists.value = response.data
    })
    .catch(error => console.error('Error:', error));
});
</script>

<style scoped>
table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  margin-top: 20px;
  font-family: 'Arial', sans-serif;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

th, td {
  padding: 8px;
  text-align: left;
}

th {
  background-color: #4CAF50;
  color: white;
  font-size: 1.2em;
  /* border-bottom: 2px solid #9CCC65; */
}

td {
  background-color: white;
}

tr:nth-child(even) td {
  background-color: #e4e4e4;
}

tr:hover td {
  background-color: #a0c4a2;
  cursor: pointer;
}

img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: contain;
}

.image-profile {
  width: 100px;
  height: 100px;
}
</style>