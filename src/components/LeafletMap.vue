<template>
  <div style="display: flex; justify-content: center;">
    <div id="map" style="height: 900px; width: 1500px;"></div>
  </div>
</template>

<script>
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { getRadius, getColor, generateCityKey } from '../utils/mapUtils.js';

export default {
  name: "LeafletMap",
  props: {
    cityData: {
      type: Array,
      default: () => []
    },
    currentYear: {
      type: Number,
      default: 2020
    },
    minPopulation: {
      type: Number,
      default: 2500
    },
    equalRadiusMode: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      map: null,
      markers: {}
    };
  },
  mounted() {
    this.initializeMap();
  },
  watch: {
    currentYear() {
      this.updateMarkers();
    },
    minPopulation() {
      this.updateMarkers();
    },
    equalRadiusMode() {
      this.updateMarkers();
    },
    cityData() {
      this.initializeMarkers();
    }
  },
  methods: {
    initializeMap() {
      this.map = L.map('map').setView([37.8, -96.9], 4);
      L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://www.carto.com/">CARTO</a>'
      }).addTo(this.map);

      // Listen for zoom changes to update marker radii
      this.map.on('zoomend', this.updateMarkerRadii);
    },

    initializeMarkers() {
      // Clear existing markers
      Object.values(this.markers).forEach(marker => {
        this.map.removeLayer(marker);
      });
      this.markers = {};

      // Add new markers
      for (const row of this.cityData) {
        const pop = row[this.currentYear] || 0;
        if (isNaN(pop) || pop < this.minPopulation) continue;
        
        const key = generateCityKey(row);
        const radius = getRadius(pop, this.map.getZoom(), this.equalRadiusMode);
        const color = getColor(pop);
        
        const marker = L.circleMarker([row.Latitude, row.Longitude], {
          radius,
          color: color,
          fillColor: color,
          fillOpacity: 0.6
        }).addTo(this.map);
        
        marker.bindPopup(`${row.City}, ${row.State}: ${pop.toLocaleString()}`);
        this.markers[key] = marker;
      }
      
      this.bringLargerMarkersToFront();
    },

    updateMarkers() {
      if (!this.map) return;

      for (const row of this.cityData) {
        const key = generateCityKey(row);
        const marker = this.markers[key];
        const pop = row[this.currentYear] || 0;
        
        if (marker) {
          if (isNaN(pop) || pop < this.minPopulation) {
            this.map.removeLayer(marker);
            delete this.markers[key];
          } else {
            const newRadius = getRadius(pop, this.map.getZoom(), this.equalRadiusMode);
            const color = getColor(pop);
            marker.setStyle({ color: color, fillColor: color });
            marker.setRadius(newRadius);
            marker.setPopupContent(`${row.City}, ${row.State}: ${pop.toLocaleString()}`);
          }
        } else if (!isNaN(pop) && pop >= this.minPopulation) {
          const color = getColor(pop);
          const newMarker = L.circleMarker([row.Latitude, row.Longitude], {
            radius: getRadius(pop, this.map.getZoom(), this.equalRadiusMode),
            color: color,
            fillColor: color,
            fillOpacity: 0.4
          }).addTo(this.map);
          newMarker.bindPopup(`${row.City}, ${row.State}: ${pop.toLocaleString()}`);
          this.markers[key] = newMarker;
        }
      }
      
      this.bringLargerMarkersToFront();
    },

    bringLargerMarkersToFront() {
      const popLookup = {};
      for (const row of this.cityData) {
        const key = generateCityKey(row);
        popLookup[key] = row[this.currentYear] || 0;
      }
      
      const sortedKeys = Object.keys(this.markers).sort((a, b) => popLookup[a] - popLookup[b]);
      for (const key of sortedKeys) {
        this.markers[key].bringToFront();
      }
    },

    updateMarkerRadii() {
      if (!this.map) return;
      
      for (const row of this.cityData) {
        const key = generateCityKey(row);
        const marker = this.markers[key];
        const pop = row[this.currentYear] || 0;
        
        if (marker && !isNaN(pop) && pop >= this.minPopulation) {
          marker.setRadius(getRadius(pop, this.map.getZoom(), this.equalRadiusMode));
        }
      }
    }
  }
};
</script>

<style>
.leaflet-container {
  width: 100%;
  height: 100%;
}
</style>