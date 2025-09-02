<template>
  <div>
    <!-- Map Container -->
    <LeafletMap
      :city-data="cityData"
      :current-year="currentYear"
      :min-population="minPopulation"
      :equal-radius-mode="equalRadiusMode"
    />

    <!-- Controls -->
    <MapControls
      v-model:min-population="minPopulation"
      v-model:equal-radius-mode="equalRadiusMode"
      v-model:current-year="currentYear"
      :start-year="startYear"
      :end-year="endYear"
      @update:current-year="debouncedYearUpdate"
    />
  </div>
</template>

<script>
import LeafletMap from './LeafletMap.vue';
import MapControls from './MapControls.vue';
import { DataService } from '../services/dataService.js';
import { debounce } from '../utils/debounce.js';

export default {
  name: "USCityMap",
  components: {
    LeafletMap,
    MapControls
  },
  data() {
    return {
      cityData: [],
      currentYear: 2020,
      startYear: 1790,
      endYear: 2020,
      minPopulation: 2500,
      equalRadiusMode: false,
      debouncedYearUpdate: null
    };
  },
  async mounted() {
    // Create debounced year update function
    this.debouncedYearUpdate = debounce((year) => {
      this.currentYear = parseInt(year);
    }, 100);

    try {
      // Load city data
      const { cityData, startYear, endYear } = await DataService.loadCityData();
      this.cityData = cityData;
      this.startYear = startYear;
      this.endYear = endYear;
      
      // Ensure current year is valid
      if (!this.isValidYear(this.currentYear)) {
        this.currentYear = endYear;
      }
    } catch (error) {
      console.error('Failed to load city data:', error);
    }
  },
  methods: {
    isValidYear(year) {
      return year >= this.startYear && year <= this.endYear;
    }
  }
};
</script>