import Papa from 'papaparse';

/**
 * Data service for loading and processing city data
 */
export class DataService {
  /**
   * Load city data from CSV file
   * @param {string} csvPath - Path to CSV file
   * @returns {Promise<{cityData: Array, startYear: number, endYear: number}>}
   */
  static async loadCityData(csvPath = '/data_files/us_city_populations_1790-2020.csv') {
    try {
      const response = await fetch(csvPath);
      const csvText = await response.text();
      const parsed = Papa.parse(csvText, { header: true, dynamicTyping: true });

      // Filter out any rows without coordinates or city/state
      const cityData = parsed.data.filter(row =>
        row.City && row.State && row.Latitude && row.Longitude
      );

      // Set startYear and endYear dynamically from columns
      const yearCols = Object.keys(parsed.data[0]).filter(k => /^\d{4}$/.test(k));
      let startYear = 1790;
      let endYear = 2020;
      
      if (yearCols.length) {
        startYear = Math.min(...yearCols.map(Number));
        endYear = Math.max(...yearCols.map(Number));
      }

      return { cityData, startYear, endYear };
    } catch (error) {
      console.error('Error loading city data:', error);
      throw error;
    }
  }
}