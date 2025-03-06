/**
 * Vuex API Cache Module
 *
 * A dedicated Vuex module for caching API responses.
 */

// Default cache TTL (time to live in milliseconds)
const DEFAULT_TTL = 5 * 60 * 1000 // 5 minutes

// TTL Configuration per endpoint type
const TTL_CONFIG = {
  LIST: 2 * 60 * 1000, // Lists: 2 minutes
  DETAIL: 5 * 60 * 1000, // Detail views: 5 minutes
  SEARCH: 1 * 60 * 1000, // Search results: 1 minute
  DROPDOWN: 15 * 60 * 1000, // Dropdown and static data: 15 minutes
  DASHBOARD: 1 * 60 * 1000, // Dashboard stats: 1 minute
  DEFAULT: 3 * 60 * 1000, // Default: 3 minutes
}

/**
 * Generate a cache key from a URL and params
 */
function generateCacheKey(url, params = {}) {
  // Sort params to ensure consistent keys regardless of object property order
  const sortedParams = Object.keys(params)
    .sort()
    .reduce((result, key) => {
      if (params[key] !== undefined && params[key] !== null) {
        result[key] = params[key]
      }
      return result
    }, {})

  const queryString =
    Object.keys(sortedParams).length > 0 ? `?${new URLSearchParams(sortedParams).toString()}` : ''

  return `${url}${queryString}`
}

const state = {
  // Store cache entries with URL-based keys
  entries: {},

  // Track when entries were cached and their expiry
  metadata: {},
}

const getters = {
  /**
   * Check if a URL is cached and not expired
   */
  isCached:
    (state) =>
    (url, params = {}) => {
      const key = generateCacheKey(url, params)
      const metadata = state.metadata[key]

      if (!metadata) return false

      // Check if cache has expired
      return Date.now() < metadata.expiry
    },

  /**
   * Get cached data for a URL if it exists and is not expired
   */
  getCachedData:
    (state, getters) =>
    (url, params = {}) => {
      const key = generateCacheKey(url, params)

      if (!getters.isCached(url, params)) {
        return null
      }

      return state.entries[key]
    },
}

const actions = {
  /**
   * Set data in the cache
   */
  setCacheData({ commit }, { url, params = {}, data, ttl = DEFAULT_TTL, cacheType = 'DEFAULT' }) {
    // Use TTL config if provided as a type, otherwise use the explicit TTL
    const effectiveTtl = ttl || TTL_CONFIG[cacheType] || TTL_CONFIG.DEFAULT

    commit('SET_CACHE_DATA', {
      key: generateCacheKey(url, params),
      data,
      expiry: Date.now() + effectiveTtl,
    })
  },

  /**
   * Remove specific data from the cache
   */
  removeCacheData({ commit }, { url, params = {} }) {
    commit('REMOVE_CACHE_DATA', {
      key: generateCacheKey(url, params),
    })
  },

  /**
   * Clear all cache entries for a specific URL (ignoring params)
   */
  clearCacheByUrl({ commit, state }, url) {
    const keysToRemove = Object.keys(state.entries).filter((key) => key.startsWith(url))

    commit('REMOVE_CACHE_KEYS', keysToRemove)
  },

  /**
   * Clear all cached data
   */
  clearAllCache({ commit }) {
    commit('CLEAR_CACHE')
  },

  /**
   * Clean up expired cache entries
   */
  cleanExpiredCache({ commit, state }) {
    const now = Date.now()
    const keysToRemove = Object.keys(state.metadata).filter(
      (key) => state.metadata[key].expiry < now,
    )

    commit('REMOVE_CACHE_KEYS', keysToRemove)
  },

  /**
   * Perform a cached API request
   */
  async fetchWithCache(
    { dispatch, getters },
    { apiCall, url, params = {}, ttl, cacheType = 'DEFAULT', forceRefresh = false },
  ) {
    // Return cached data if it exists and we're not forcing a refresh
    if (!forceRefresh && getters.isCached(url, params)) {
      return getters.getCachedData(url, params)
    }

    // Otherwise make the API call and cache the result
    const data = await apiCall()

    // Cache the result
    dispatch('setCacheData', {
      url,
      params,
      data,
      ttl,
      cacheType,
    })

    return data
  },
}

const mutations = {
  SET_CACHE_DATA(state, { key, data, expiry }) {
    // Use Vue.set for reactivity when adding new properties
    state.entries = { ...state.entries, [key]: data }
    state.metadata = { ...state.metadata, [key]: { timestamp: Date.now(), expiry } }
  },

  REMOVE_CACHE_DATA(state, { key }) {
    const entries = { ...state.entries }
    const metadata = { ...state.metadata }

    delete entries[key]
    delete metadata[key]

    state.entries = entries
    state.metadata = metadata
  },

  REMOVE_CACHE_KEYS(state, keys) {
    if (keys.length === 0) return

    const entries = { ...state.entries }
    const metadata = { ...state.metadata }

    keys.forEach((key) => {
      delete entries[key]
      delete metadata[key]
    })

    state.entries = entries
    state.metadata = metadata
  },

  CLEAR_CACHE(state) {
    state.entries = {}
    state.metadata = {}
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
