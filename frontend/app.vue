<template>
  <div>
    <!-- <NuxtWelcome /> -->
    <h1>Test</h1>
    <div>
    <!-- <div v-for="item in items" :key="item.id">
      {{ item.name }}
    </div> -->
  </div>
  </div>
</template>

<script setup lang="ts">
// import { ref, onMounted } from 'vue';
import axios from 'axios';

const artists = ref([]);

onMounted(async () => {
  console.log('onMounted: ');
  // const response = await axios.get('http://localhost:8000/api/items');
  // let data;

  axios.get('http://localhost:8000/artists/')
    .then(response => {
      console.log('response: ', response);
      artists.value = response.data
    })
    .catch(error => console.error('Error:', error));
});
</script>