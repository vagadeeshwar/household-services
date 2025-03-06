import { service } from '@/services'

const state = {
  services: [],
  selectedService: null,
  loading: false,
  error: null,
  pagination: {
    currentPage: 1,
    totalPages: 0,
    perPage: 10,
  },
}

const getters = {
  allServices: (state) => state.services,
  selectedService: (state) => state.selectedService,
  isLoading: (state) => state.loading,
  error: (state) => state.error,
  pagination: (state) => state.pagination,
}

const actions = {
  async fetchActiveServices({ commit }, params = {}) {
    try {
      commit('SET_LOADING', true)
      const response = await service.getActive(params)
      commit('SET_SERVICES', response.data)
      commit('SET_PAGINATION', response.pagination)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  async fetchAllServices({ commit }, params = {}) {
    try {
      commit('SET_LOADING', true)
      const response = await service.getAll(params)
      commit('SET_SERVICES', response.data)
      commit('SET_PAGINATION', response.pagination)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchActiveServiceById({ commit }, id) {
    try {
      commit('SET_LOADING', true)
      const response = await service.getActiveById(id)
      commit('SET_SELECTED_SERVICE', response)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchAllServiceById({ commit }, id) {
    try {
      commit('SET_LOADING', true)
      const response = await service.getAllById(id)
      commit('SET_SELECTED_SERVICE', response)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async createService({ commit }, data) {
    try {
      commit('SET_LOADING', true)
      const response = await service.create(data)
      commit('ADD_SERVICE', response)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateService({ commit }, { id, data }) {
    try {
      commit('SET_LOADING', true)
      const response = await service.update(id, data)
      commit('UPDATE_SERVICE', response)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async toggleService({ commit }, id) {
    try {
      commit('SET_LOADING', true)
      const response = await service.toggle(id)
      commit('UPDATE_SERVICE', response)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async deleteService({ commit }, id) {
    try {
      commit('SET_LOADING', true)
      await service.delete(id)
      commit('REMOVE_SERVICE', id)
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
}

const mutations = {
  SET_SERVICES(state, services) {
    state.services = services
  },

  SET_SELECTED_SERVICE(state, service) {
    state.selectedService = service
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

  ADD_SERVICE(state, service) {
    state.services.unshift(service)
  },

  UPDATE_SERVICE(state, updatedService) {
    const index = state.services.findIndex((s) => s.id === updatedService.id)
    if (index !== -1) {
      state.services.splice(index, 1, updatedService)
    }
  },

  REMOVE_SERVICE(state, id) {
    state.services = state.services.filter((s) => s.id !== id)
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
