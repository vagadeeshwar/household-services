import { professional } from '@/services'

const state = {
  professionals: [],
  selectedProfessional: null,
  loading: false,
  error: null,
  pagination: {
    currentPage: 1,
    totalPages: 0,
    perPage: 10,
  },
}

const getters = {
  allProfessionals: (state) => state.professionals,
  selectedProfessional: (state) => state.selectedProfessional,
  isLoading: (state) => state.loading,
  error: (state) => state.error,
  pagination: (state) => state.pagination,
}

const actions = {
  async fetchProfessionals({ commit }, { params = {}, forceRefresh = false } = {}) {
    try {
      commit('SET_LOADING', true)
      const response = await professional.getAll(params, forceRefresh)
      commit('SET_PROFESSIONALS', response.data)
      commit('SET_PAGINATION', response.pagination)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchProfessionalById({ commit }, { params = {}, forceRefresh = false, id }) {
    try {
      commit('SET_LOADING', true)
      const response = await professional.getById(id, params, forceRefresh)
      commit('SET_SELECTED_PROFESSIONAL', response)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async verifyProfessional({ commit }, { id }) {
    try {
      commit('SET_LOADING', true)
      const response = await professional.verify(id)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async blockProfessional({ commit }, { id, data }) {
    try {
      commit('SET_LOADING', true)
      const response = await professional.block(id, data)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async unblockProfessional({ commit }, { id }) {
    try {
      commit('SET_LOADING', true)
      const response = await professional.unblock(id)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchReviews({ commit }, { params = {} } = {}) {
    try {
      commit('SET_LOADING', true)
      const response = await professional.getReviews(params)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateDocument({ commit }, { data }) {
    try {
      commit('SET_LOADING', true)
      const response = await professional.updateDocument(data)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async downloadDocument({ commit }) {
    try {
      commit('SET_LOADING', true)
      const response = await professional.downloadDocument()
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateService({ commit }, { data }) {
    try {
      commit('SET_LOADING', true)
      const response = await professional.updateService(data)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  async getDashboard({ commit }, { params = {}, forceRefresh = false } = {}) {
    try {
      commit('SET_LOADING', true)
      const response = await professional.getDashboard(params, forceRefresh)
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
  SET_PROFESSIONALS(state, professionals) {
    state.professionals = professionals
  },

  SET_SELECTED_PROFESSIONAL(state, professional) {
    state.selectedProfessional = professional
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
