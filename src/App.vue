<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-auto text-center">
        <h1 class="display-4 my-4" style="font-family: 'Segoe UI', 'Arial', sans-serif;">
          Population Map of the United States (1790-2020)
        </h1>
        <USMap />
      </div>
    </div>
  </div>
</template>

<script>
import USMap from "./components/USMap.vue";

export default {
  components: { USMap }
};
</script>