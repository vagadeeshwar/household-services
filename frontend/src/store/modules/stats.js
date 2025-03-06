import { stats } from '@/services'

const state = {
  loading: false,
  error: null,
  pagination: {
    currentPage: 1,
    totalPages: 0,
    perPage: 10,
  },
}

const getters = {
  isLoading: (state) => state.loading,
  error: (state) => state.error,
  pagination: (state) => state.pagination,
}

const actions = {
  async fetchActivityLogs({ commit }, params = {}) {
    try {
      commit('SET_LOADING', true)
      const response = await stats.getActivityLogs(params)
      commit('SET_PAGINATION', response.meta)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  async fetchOthersActivityLogs({ commit }, { id, ...params } = {}) {
    try {
      commit('SET_LOADING', true)
      const response = await stats.getOthersActivityLogs(id, params)
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
