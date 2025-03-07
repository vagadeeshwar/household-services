/**
 * Enhanced API Service with Vuex-based Caching
 */

import api from './api'
import store from '@/store'

/**
 * Extended API with Vuex caching capabilities
 */
const cachedApi = {
  /**
   * Perform a GET request with caching
   *
   * @param {string} url - API endpoint
   * @param {object} options - Request options
   * @param {object} options.params - URL parameters
   * @param {number} options.ttl - Custom time-to-live in milliseconds
   * @param {boolean} options.forceRefresh - Force a refresh of the cache
   * @param {string} options.cacheType - Type of cache (used for TTL config)
   * @returns {Promise<any>} - API response data
   */
  async get(url, { params = {}, ttl, forceRefresh = false, cacheType = 'DEFAULT' } = {}) {
    console.debug('Cache request for:', url, params)

    return store.dispatch('apiCache/fetchWithCache', {
      apiCall: () => api.get(url, { params }).then((response) => response.data),
      url,
      params,
      ttl,
      cacheType,
      forceRefresh,
    })
  },

  /**
   * Perform a GET request for paginated data with caching
   *
   * @param {string} url - API endpoint
   * @param {object} params - URL parameters (including pagination)
   * @param {object} options - Cache options
   * @returns {Promise<any>} - API response data with pagination
   */
  async getPaginated(url, params = {}, { ttl, forceRefresh = false } = {}) {
    forceRefresh = forceRefresh === true

    return this.get(url, {
      params,
      ttl,
      forceRefresh,
      cacheType: 'LIST',
    })
  },

  /**
   * Fetch a single resource by ID with caching
   *
   * @param {string} url - API endpoint with ID
   * @param {object} options - Cache options
   * @returns {Promise<any>} - API response data
   */
  async getById(url, { ttl, forceRefresh = false } = {}) {
    forceRefresh = forceRefresh === true

    return this.get(url, {
      ttl,
      forceRefresh,
      cacheType: 'DETAIL',
    })
  },

  /**
   * Perform a POST request and invalidate related cache
   *
   * @param {string} url - API endpoint
   * @param {object} data - Request payload
   * @param {object} config - Axios config
   * @returns {Promise<any>} - API response data
   */
  async post(url, data, config = {}) {
    const response = await api.post(url, data, config)
    // Clear cache for this URL since data has changed
    store.dispatch('apiCache/clearCacheByUrl', url)
    return response.data
  },

  /**
   * Perform a PUT request and invalidate related cache
   *
   * @param {string} url - API endpoint
   * @param {object} data - Request payload
   * @param {object} config - Axios config
   * @returns {Promise<any>} - API response data
   */
  async put(url, data, config = {}) {
    const response = await api.put(url, data, config)
    // Clear cache for this URL since data has changed
    store.dispatch('apiCache/clearCacheByUrl', url)
    return response.data
  },

  /**
   * Perform a DELETE request and invalidate related cache
   *
   * @param {string} url - API endpoint
   * @param {object} config - Axios config
   * @returns {Promise<any>} - API response data
   */
  async delete(url, config = {}) {
    const response = await api.delete(url, config)
    // Clear cache for this URL since data has changed
    store.dispatch('apiCache/clearCacheByUrl', url)
    return response.data
  },

  /**
   * Upload a file with attached form data
   *
   * @param {string} url - API endpoint
   * @param {File} file - File to upload
   * @param {string} fieldName - Form field name for the file
   * @param {string} method - HTTP method (PUT or POST)
   * @returns {Promise<any>} - API response data
   */
  async uploadFile(url, file, fieldName = 'file', method = 'POST') {
    const formData = new FormData()
    formData.append(fieldName, file)

    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }

    const response =
      method.toUpperCase() === 'PUT'
        ? await api.put(url, formData, config)
        : await api.post(url, formData, config)

    // Clear cache for this URL since data has changed
    store.dispatch('apiCache/clearCacheByUrl', url)
    return response.data
  },

  /**
   * Check if data for a URL is cached and valid
   */
  isCached(url, params = {}) {
    return store.getters['apiCache/isCached'](url, params)
  },

  /**
   * Get cached data for a URL, if it exists
   */
  getCached(url, params = {}) {
    return store.getters['apiCache/getCachedData'](url, params)
  },

  /**
   * Manually cache data for a URL
   */
  setCache(url, params = {}, data, ttl, cacheType = 'DEFAULT') {
    store.dispatch('apiCache/setCacheData', { url, params, data, ttl, cacheType })
  },

  /**
   * Force invalidation of cache for a URL
   */
  invalidateCache(url) {
    store.dispatch('apiCache/clearCacheByUrl', url)
  },

  /**
   * Clear all cache
   */
  clearAllCache() {
    store.dispatch('apiCache/clearAllCache')
  },

  /**
   * Original axios instance for when you need direct access
   */
  axios: api,
}

// Clean expired cache entries every minute
setInterval(() => {
  store.dispatch('apiCache/cleanExpiredCache')
}, 60 * 1000)

export default cachedApi
