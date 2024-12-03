import { stats } from '@/services'

const state = {
  dashboardStats: null,
  detailedStats: [],
  loading: false,
  error: null,
  pagination: {
    currentPage: 1,
    totalPages: 0,
    perPage: 10,
  },
}

const getters = {
  dashboardStats: (state) => state.dashboardStats,
  detailedStats: (state) => state.detailedStats,
  isLoading: (state) => state.loading,
  error: (state) => state.error,
  pagination: (state) => state.pagination,
}

const actions = {
  async fetchDashboardStats({ commit }) {
    try {
      commit('SET_LOADING', true)
      const response = await stats.getDashboard()
      commit('SET_DASHBOARD_STATS', response)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchDetailedStats({ commit }, params = {}) {
    try {
      commit('SET_LOADING', true)
      const response = await stats.getDetailed(params)
      commit('SET_DETAILED_STATS', response.data)
      commit('SET_PAGINATION', response.meta)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
}

const mutations = {
  SET_DASHBOARD_STATS(state, stats) {
    state.dashboardStats = stats
  },

  SET_DETAILED_STATS(state, stats) {
    state.detailedStats = stats
  },

  SET_LOADING(state, loading) {
    state.loading = loading
  },

  SET_ERROR(state, error) {
    state.error = error
  },

  SET_PAGINATION(state, pagination) {
    state.pagination = pagination
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
