<template>
  <div>
    <h1 v-pre>their imagination</h1>
    <div>
    <table>
      <thead>
        <tr>
          <th>[][][][][][][]</th>
          <th>|||||||||||||||||||||</th>
          <th> - - - - - - - - - - -</th>
          <th>++++++++++</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="artist in artists" :key="artist.id">
          <td class="profile-image-containter">
            <img class="profile-image" :src="artist.profile_image" :alt="artist.name" />
          </td>
          <td>{{ artist.name }}</td>
          <td>
              <img class="artwork-image" v-for="(artwork, index) in artist.artworks.slice(0, 5)" :alt="artwork.title" :key="index" :src="artwork.picture"/>
          </td>
          <td>{{ artist.notes }}</td>
        </tr>
      </tbody>
    </table>
  </div>
  </div>
</template>

<script setup lang="ts">
import axios from 'axios';
const artists = ref<any>([]);

onMounted(async () => {

  axios.get('http://localhost:8000/artists/')
    .then(response => {
      console.log('response: ', response);
      console.log('response.data: ', response.data);
      artists.value = response.data
    })
    .catch(error => console.error('Error:', error));
});


// const setRandomColor = (event: any) => {
//   event.target.style.backgroundColor = getRandomColor();
// };

// const getRandomColor = () => {
//   const letters = '0123456789ABCDEF';
//   let color = '#';
//   for (let i = 0; i < 6; i++) {
//     color += letters[Math.floor(Math.random() * 16)];
//   }
//   return color;
// };

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
  background-color: #c7f2ff;
  /* cursor: pointer; */
}

.profile-image {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: contain;
}

.profile-image-containter {
  width: 100px;
  height: 100px;
}

.artwork-image {
  width: 100px;
  height: 100px;
  object-fit: contain;
}

</style>