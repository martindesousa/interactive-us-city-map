<template>
  <div>
    <!-- Centered Map Container -->
    <div style="display: flex; justify-content: center;">
      <div id="map" style="height: 900px; width: 1500px;"></div>
    </div>

    <div class="container mt-4">
      <div class="row justify-content-center">
        <div class="col-auto">
          <!-- Stack controls vertically -->
          <div class="d-flex flex-column align-items-center">
            <!-- Row: Min Population + Checkbox -->
            <div class="d-flex flex-row align-items-center mb-2">
              <!-- Minimum Population Filter -->
              <label class="form-label mb-0 me-3">
                Minimum Population:
                <input
                  type="number"
                  v-model.number="minPopulation"
                  min="0"
                  step="500"
                  class="form-control d-inline-block ms-2"
                  style="width: 120px;"
                />
              </label>
              <!-- Equal Radius Checkbox -->
              <div class="form-check ms-3">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="equalRadius"
                  v-model="equalRadiusMode"
                  @change="updateMarkers"
                />
                <label class="form-check-label" for="equalRadius">
                  Equal Dot Sizes
                </label>
              </div>
            </div>
            <!-- Slider and Year Label below -->
            <input
              type="range"
              :min="startYear"
              :max="endYear"
              v-model.number="currentYear"
              @input="debouncedUpdateMarkers"
              step="10"
              class="form-range"
              style="width: 600px;"
            />
            <div class="fw-bold fs-2 mt-2">
              Year: {{ currentYear }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import Papa from 'papaparse'; 

function debounce(func, delay) { // Debouncer for functions (used for updateMarkers to ensure smooth slider usage)
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), delay);
  };
}

export default {
  name: "USCityGrowthMap",
  data() {
    return {
      map: null,
      markers: {},
      cityData: [],        // array of city objects
      currentYear: 2020,
      startYear: 1790,
      endYear: 2020,
      radiusScale: 0.0003,
      minPopulation: 2500,
      debouncedUpdateMarkers: null, // debounced updateMarkers function
      equalRadiusMode: false,
    };
  },
  mounted() {
    // Initialize map
    this.map = L.map('map').setView([37.8, -96.9], 4);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://www.carto.com/">CARTO</a>'
    }).addTo(this.map);

    // Listen for zoom changes to update marker radii
    this.map.on('zoomend', this.updateMarkerRadii);

    // Debounce the updateMarkers method
    this.debouncedUpdateMarkers = debounce(this.updateMarkers, 100);

    // Load city data
    this.loadCityData().then(() => {
      this.initializeMarkers();
    });

  },
  methods: {
    async loadCityData() { // Load city data from CSV
      const response = await fetch('/data_files/us_city_populations_1790-2020.csv'); // Fetch the CSV
      const csvText = await response.text();
      const parsed = Papa.parse(csvText, { header: true, dynamicTyping: true });

      // Filter out any rows without coordinates or city/state
      this.cityData = parsed.data.filter(row =>
        row.City && row.State && row.Latitude && row.Longitude
      );

      // Set startYear and endYear dynamically from columns (just cause)
      const yearCols = Object.keys(parsed.data[0]).filter(k => /^\d{4}$/.test(k));
      if (yearCols.length) {
        this.startYear = Math.min(...yearCols.map(Number));
        this.endYear = Math.max(...yearCols.map(Number));
        if (!yearCols.includes(this.currentYear.toString())) {
          this.currentYear = this.endYear;
        }
      }
    },
    getRadius(pop) { // Get the radius of the marker based on population

      const zoom = this.map ? this.map.getZoom() : 4;
      let base;
      if (this.equalRadiusMode)
      {
         base = 1;
      }
      else 
      {
        if (pop >= 10000000) {
          base = 11;
        } else if (pop >= 5000000) {
          base = 9;
        } else if (pop >= 1000000) {
          base = 7.5;
        } else if (pop >= 500000) {
          base = 6;
        } else if (pop >= 250000) {
          base = 4.5;
        } else if (pop >= 100000) {
          base = 3.5;
        } else if (pop >= 50000) {
          base = 2.5;
        } else if (pop >= 10000) {
          base = 2;
        } else if (pop >= 5000) {
          base = 1;
        } else if (pop >= 2500) {
          base = 0.7;
        } else {
          base = 1;
        }
      }
      // Scale radius with zoom
      return base * Math.pow(1.4, zoom - 4);

    },

    getColor(pop) { // Define population breakpoints and corresponding colors

      if (pop >= 5000000) return "#800026"; // deep red
      if (pop >= 1000000)  return "#800026"; // deep red
      if (pop >= 500000)   return "#BD0026"; // red
      if (pop >= 100000)   return "#E31A1C"; // orange-red
      if (pop >= 50000)    return "#E31A1C"; // orange-red
      if (pop >= 10000)    return "#FD8D3C"; // orange
      if (pop >= 5000)     return "#FEB24C"; // yellow-orange
      return "#FED976"; // yellow for smallest

    },

    initializeMarkers() { // Initialize markers for each city
      for (const row of this.cityData) {
        const pop = row[this.currentYear] || 0;
        if (isNaN(pop) || pop < this.minPopulation) continue;
        const key = `${row.City},${row.State},${row.Latitude},${row.Longitude}`;
        const radius = this.getRadius(pop);
        const color = this.getColor(pop);
        const marker = L.circleMarker([row.Latitude, row.Longitude], {
          radius,
          color: color,
          fillColor: color,
          fillOpacity: 0.6
        }).addTo(this.map);
        marker.bindPopup(`${row.City}, ${row.State}: ${pop.toLocaleString()}`);
        this.markers[key] = marker;
      }
      // Bring larger markers to front
      this.bringLargerMarkersToFront();
    },

    updateMarkers() { // Update markers for each city after user interaction changes
      for (const row of this.cityData) {
        const key = `${row.City},${row.State},${row.Latitude},${row.Longitude}`;
        const marker = this.markers[key];
        const pop = row[this.currentYear] || 0;
        if (marker) {
          if (isNaN(pop) || pop < this.minPopulation) {
            this.map.removeLayer(marker);
            delete this.markers[key];
          } else {
            const newRadius = this.getRadius(pop);
            const color = this.getColor(pop);
            marker.setStyle({ color: color, fillColor: color });
            marker.setRadius(newRadius);
            marker.setPopupContent(`${row.City}, ${row.State}: ${pop.toLocaleString()}`);
          }
        } else if (!isNaN(pop) && pop >= this.minPopulation) {
          const color = this.getColor(pop);
          const newMarker = L.circleMarker([row.Latitude, row.Longitude], {
            radius: this.getRadius(pop),
            color: color,
            fillColor: color,
            fillOpacity: 0.4
          }).addTo(this.map);
          newMarker.bindPopup(`${row.City}, ${row.State}: ${pop.toLocaleString()}`);
          this.markers[key] = newMarker;
        }
      }
      // Bring larger markers to front
      this.bringLargerMarkersToFront();
    },

    bringLargerMarkersToFront() {
      const popLookup = {};
      for (const row of this.cityData) {
        const key = `${row.City},${row.State},${row.Latitude},${row.Longitude}`;
        popLookup[key] = row[this.currentYear] || 0;
      }
      const sortedKeys = Object.keys(this.markers).sort((a, b) => popLookup[a] - popLookup[b]);
      for (const key of sortedKeys) {
        this.markers[key].bringToFront();
      }
    },
    updateMarkerRadii() { // Update marker radii for each zoom
        for (const row of this.cityData) {
          const key = `${row.City},${row.State},${row.Latitude},${row.Longitude}`;
          const marker = this.markers[key];
          const pop = row[this.currentYear] || 0;
          if (marker && !isNaN(pop) && pop >= this.minPopulation) {
            marker.setRadius(this.getRadius(pop));
          }
        }
    },
  },
  watch: { // Watch for changes in minPopulation user input
      minPopulation() {
        this.debouncedUpdateMarkers();
      }
    },
};
</script>

<style>
/* Optional: ensure leaflet tiles display properly */
.leaflet-container {
  width: 100%;
  height: 100%;
  }
</style>