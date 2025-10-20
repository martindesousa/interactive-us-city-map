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
      type: [Number, String],
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
      canvasRenderer: null,
      markerCache: {},
      keyToRow: {},
      updateTimer: null, // debounce timer for rapid changes
      LARGE_CITY_THRESHOLD: 100000 // only re-order cities above 100k population
    };
  },
  computed: {
    numericCurrentYear() {
      const n = Number(this.currentYear);
      return Number.isNaN(n) ? 0 : n;
    }
  },
  mounted() {
    this.initializeMap();
  },
  watch: {
    currentYear() {
      this.debouncedUpdateMarkers();
    },
    minPopulation() {
      this.debouncedUpdateMarkers();
    },
    equalRadiusMode() {
      this.debouncedUpdateMarkerRadii();
    },
    cityData() {
      this.updateMarkers();
    }
  },
  beforeUnmount() {
    // clean up
    if (this.updateTimer) clearTimeout(this.updateTimer);
    if (this.map) {
      this.map.off();
      this.map.remove();
    }
  },
  methods: {
    // debounce updates when slider is being dragged (avoids multiple rapid updates)
    debouncedUpdateMarkers() {
      if (this.updateTimer) clearTimeout(this.updateTimer);
      this.updateTimer = setTimeout(() => {
        this.updateMarkers();
      }, 40); // 40ms debounce
    },

    debouncedUpdateMarkerRadii() {
      if (this.updateTimer) clearTimeout(this.updateTimer);
      this.updateTimer = setTimeout(() => {
        this.updateMarkerRadii();
      }, 50);
    },

    initializeMap() {
      this.map = L.map('map', { preferCanvas: true }).setView([37.8, -96.9], 4);

      L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://www.carto.com/">CARTO</a>',
        updateWhenIdle: true, // only update tiles when map stops moving
        keepBuffer: 2 // reduce tile buffer for faster rendering
      }).addTo(this.map);

      this.canvasRenderer = L.canvas({ 
        padding: 0.5,
        tolerance: 5 // increase click tolerance for better performance
      });

      // update marker radii on zoom
      this.map.on('zoomend', this.debouncedUpdateMarkerRadii);

      this.updateMarkers();
    },

    // smart update: only add/remove/update markers that changed
    updateMarkers() {
      if (!this.map) return;

      // batch DOM updates with requestAnimationFrame for smoother rendering
      requestAnimationFrame(() => {
        this.performMarkerUpdate();
      });
    },
    
    performMarkerUpdate() {
      // build lookup of current population by key
      const currentPopLookup = {};
      const newKeyToRow = {};

      for (const row of this.cityData) {
        const pop = row[this.numericCurrentYear] || 0;
        const key = generateCityKey(row);
        currentPopLookup[key] = pop;
        newKeyToRow[key] = row;
      }

      // batch marker removals
      const toRemove = [];
      for (const key of Object.keys(this.markerCache)) {
        const pop = currentPopLookup[key] || 0;
        if (isNaN(pop) || pop < this.minPopulation) {
          toRemove.push(key);
        }
      }
      
      // remove in one batch
      toRemove.forEach(key => {
        this.map.removeLayer(this.markerCache[key].marker);
        delete this.markerCache[key];
      });

      // batch marker additions
      const toAdd = [];
      const toUpdate = [];
      
      for (const key in currentPopLookup) {
        const pop = currentPopLookup[key];
        if (isNaN(pop) || pop < this.minPopulation) continue;

        const row = newKeyToRow[key];
        const cached = this.markerCache[key];

        if (cached) {
          toUpdate.push({ key, row, pop, cached });
        } else {
          toAdd.push({ key, row, pop });
        }
      }
      
      // update existing markers
      toUpdate.forEach(({ key, row, pop, cached }) => {
        const color = getColor(pop);
        cached.marker.setStyle({ color, fillColor: color });
        cached.marker.setRadius(getRadius(pop, this.map.getZoom(), this.equalRadiusMode));
        cached.pop = pop;
        cached.row = row;
        
        // update popup content (rebind with new year data)
        const yearVal = row[this.numericCurrentYear] || 0;
        const popupContent = `${row.City}, ${row.State}: ${yearVal.toLocaleString()}`;
        
        // if popup is already bound, update it
        if (cached.marker.getPopup()) {
          cached.marker.setPopupContent(popupContent);
        }
      });
      
      // add new markers
      toAdd.sort((a, b) => a.pop - b.pop);
      toAdd.forEach(({ key, row, pop }) => {
        const marker = this.createCityMarker(row, pop);
        marker.addTo(this.map);
        this.markerCache[key] = { marker, row, pop };
      });
      
      // bring all large cities to front in sorted order (smallest to largest)
      const allLargeCities = [];
      for (const key in this.markerCache) {
        const cached = this.markerCache[key];
        if (cached.pop >= this.LARGE_CITY_THRESHOLD) {
          allLargeCities.push({ key, pop: cached.pop });
        }
      }
      
      allLargeCities.sort((a, b) => a.pop - b.pop);
      allLargeCities.forEach(({ key }) => {
        this.markerCache[key].marker.bringToFront();
      });
      
      this.keyToRow = newKeyToRow;
    },

    createCityMarker(row, pop) {
      const color = getColor(pop);
      const radius = getRadius(pop, this.map ? this.map.getZoom() : 4, this.equalRadiusMode);

      const marker = L.circleMarker([row.Latitude, row.Longitude], {
        renderer: this.canvasRenderer,
        radius,
        color,
        fillColor: color,
        fillOpacity: 0.6,
        weight: 1,
        interactive: true
      });

      // bind popup so it can be updated later
      const yearVal = row[this.numericCurrentYear] || 0;
      marker.bindPopup(`${row.City}, ${row.State}: ${yearVal.toLocaleString()}`);

      return marker;
    },

    updateMarkerRadii() {
      if (!this.map) return;

      // batch radius updates with requestAnimationFrame
      requestAnimationFrame(() => {
        const zoom = this.map.getZoom();
        for (const key in this.markerCache) {
          const cached = this.markerCache[key];
          const pop = cached.pop || 0;
          if (!isNaN(pop) && pop >= this.minPopulation) {
            cached.marker.setRadius(getRadius(pop, zoom, this.equalRadiusMode));
          }
        }
      });
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