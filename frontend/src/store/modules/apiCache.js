/**
 * Vuex API Cache Module
 *
 * A dedicated Vuex module for caching API responses.
 */

// Default cache TTL (time to live in milliseconds)
const DEFAULT_TTL = 5 * 60 * 1000 // 5 minutes

// TTL Configuration per endpoint type
const TTL_CONFIG = {
  LIST: 3 * 60 * 1000, // Lists: 3 minutes
  DETAIL: 3 * 60 * 1000, // Detail views: 3 minutes
  SEARCH: 3 * 60 * 1000, // Search results: 3 minutes
  DROPDOWN: 3 * 60 * 1000, // Dropdown and static data: 3 minutes
  DASHBOARD: 3 * 60 * 1000, // Dashboard stats: 3 minutes
  DEFAULT: 3 * 60 * 1000, // Default: 3 minutes
}

/**
 * Generate a cache key from a URL and params
 */
function generateCacheKey(url, params = {}) {
  // Create a new object to avoid reference issues
  const cleanedParams = {}

  // Process parameters to ensure consistent serialization
  Object.keys(params)
    .sort()
    .forEach((key) => {
      const value = params[key]
      if (value !== undefined && value !== null) {
        // Handle Date objects consistently
        if (value instanceof Date) {
          cleanedParams[key] = value.toISOString().split('T')[0] // Use consistent YYYY-MM-DD format
        } else if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}/.test(value)) {
          // Standardize date strings to just the date portion (strip time if present)
          if (value.includes('T')) {
            cleanedParams[key] = value.split('T')[0]
          } else {
            cleanedParams[key] = value
          }
        } else {
          cleanedParams[key] = value
        }
      }
    })

  // Create a consistent query string
  const queryParams = new URLSearchParams()
  Object.keys(cleanedParams)
    .sort()
    .forEach((key) => {
      queryParams.append(key, cleanedParams[key])
    })

  const queryString = queryParams.toString() ? `?${queryParams.toString()}` : ''

  // Debug logging (remove in production)
  console.debug(`Cache key generated for ${url}${queryString}`)

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

      if (!metadata) {
        console.debug(`Cache check: MISS - Key not found: ${key}`)
        return false
      }

      // Check if cache has expired
      const isValid = Date.now() < metadata.expiry
      console.debug(`Cache check: ${isValid ? 'HIT' : 'EXPIRED'} - Key: ${key}`, {
        now: new Date(),
        expiry: new Date(metadata.expiry),
        ttlRemaining: Math.round((metadata.expiry - Date.now()) / 1000) + 's',
      })

      return isValid
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

      const data = state.entries[key]
      console.debug(`Returning cached data for: ${key}`)
      return data
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
    { getters, commit },
    { apiCall, url, params = {}, ttl, cacheType = 'DEFAULT', forceRefresh = false },
  ) {
    // Generate cache key
    const cacheKey = generateCacheKey(url, params)

    // Log cache hit/miss
    console.debug(`Cache request for ${url}`, {
      params,
      cacheKey,
      cacheExists: getters.isCached(url, params),
      forceRefresh,
    })
    // Return cached data if it exists and we're not forcing a refresh
    if (!forceRefresh && getters.isCached(url, params)) {
      console.debug('✅ Cache HIT:', cacheKey)
      return getters.getCachedData(url, params)
    }

    console.debug('❌ Cache MISS:', cacheKey)

    // Otherwise make the API call and cache the result
    const data = await apiCall()

    // Cache the result - use explicit key to ensure consistency
    const effectiveTtl = ttl || TTL_CONFIG[cacheType] || TTL_CONFIG.DEFAULT

    commit('SET_CACHE_DATA', {
      key: cacheKey,
      data,
      expiry: Date.now() + effectiveTtl,
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
