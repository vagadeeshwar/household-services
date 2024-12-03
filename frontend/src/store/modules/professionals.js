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
  async fetchProfessionals({ commit }, params = {}) {
    try {
      commit('SET_LOADING', true)
      const response = await professional.getAll(params)
      commit('SET_PROFESSIONALS', response.data)
      commit('SET_PAGINATION', response.meta)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchProfessionalById({ commit }, id) {
    try {
      commit('SET_LOADING', true)
      const response = await professional.getById(id)
      commit('SET_SELECTED_PROFESSIONAL', response)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async verifyProfessional({ commit }, id) {
    try {
      commit('SET_LOADING', true)
      const response = await professional.verify(id)
      commit('UPDATE_PROFESSIONAL', response)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async blockProfessional({ commit }, { id, reason }) {
    try {
      commit('SET_LOADING', true)
      const response = await professional.block(id, reason)
      commit('UPDATE_PROFESSIONAL', response)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchDashboard({ commit }) {
    try {
      commit('SET_LOADING', true)
      const response = await professional.getDashboard()
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchReviews({ commit }, params = {}) {
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

  async updateDocument({ commit }, document) {
    try {
      commit('SET_LOADING', true)
      const response = await professional.updateDocument(document)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateService({ commit }, serviceTypeId) {
    try {
      commit('SET_LOADING', true)
      const response = await professional.updateService(serviceTypeId)
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

  UPDATE_PROFESSIONAL(state, updatedProfessional) {
    const index = state.professionals.findIndex((p) => p.id === updatedProfessional.id)
    if (index !== -1) {
      state.professionals.splice(index, 1, updatedProfessional)
    }
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
