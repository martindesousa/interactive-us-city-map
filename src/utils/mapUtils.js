/**
 * Map utility functions for population visualization
 */

/**
 * Get marker radius based on population and zoom level
 * @param {number} pop - Population value
 * @param {number} zoom - Current map zoom level
 * @param {boolean} equalRadiusMode - Whether to use equal radius for all markers
 * @returns {number} Marker radius
 */
export function getRadius(pop, zoom, equalRadiusMode = false) {
  let base;
  
  if (equalRadiusMode) {
    base = 1;
  } else {
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
}

/**
 * Get color based on population value
 * @param {number} pop - Population value
 * @returns {string} Hex color code
 */
export function getColor(pop) {
  if (pop >= 5000000) return "#800026"; // deep red
  if (pop >= 1000000) return "#800026"; // deep red
  if (pop >= 500000) return "#BD0026"; // red
  if (pop >= 100000) return "#E31A1C"; // orange-red
  if (pop >= 50000) return "#E31A1C"; // orange-red
  if (pop >= 10000) return "#FD8D3C"; // orange
  if (pop >= 5000) return "#FEB24C"; // yellow-orange
  return "#FED976"; // yellow for smallest
}

/**
 * Generate unique key for city marker
 * @param {Object} cityRow - City data row
 * @returns {string} Unique key
 */
export function generateCityKey(cityRow) {
  return `${cityRow.City},${cityRow.State},${cityRow.Latitude},${cityRow.Longitude}`;
}