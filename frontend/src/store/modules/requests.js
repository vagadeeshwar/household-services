import { request } from '@/services'

const state = {
  requests: [],
  selectedRequest: null,
  loading: false,
  error: null,
  pagination: {
    currentPage: 1,
    totalPages: 0,
    perPage: 10,
  },
}

const getters = {
  allRequests: (state) => state.requests,
  selectedRequest: (state) => state.selectedRequest,
  isLoading: (state) => state.loading,
  error: (state) => state.error,
  pagination: (state) => state.pagination,
  requestsByStatus: (state) => (status) => {
    return state.requests.filter((request) => request.status === status)
  },
}

const actions = {
  async createRequest({ commit }, { data }) {
    try {
      commit('SET_LOADING', true)
      const response = await request.create(data)
      commit('ADD_REQUEST', response)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchProfessionalRequests({ commit }, { params = {}, forceRefresh = false } = {}) {
    try {
      commit('SET_LOADING', true)
      const response = await request.getProfessionalRequests(params, forceRefresh)
      commit('SET_REQUESTS', response.data)
      commit('SET_PAGINATION', response.pagination)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchProfessionalRequestsById({ commit }, { id, params = {}, forceRefresh = false }) {
    try {
      commit('SET_LOADING', true)
      const response = await request.getProfessionalRequestsById(id, params, forceRefresh)
      commit('SET_REQUESTS', response.data)
      commit('SET_PAGINATION', response.pagination)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchCustomerRequests({ commit }, { params = {}, forceRefresh = false } = {}) {
    try {
      commit('SET_LOADING', true)
      const response = await request.getCustomerRequests(params, forceRefresh)
      commit('SET_REQUESTS', response.data)
      commit('SET_PAGINATION', response.pagination)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchCustomerRequestsById({ commit }, { id, params = {}, forceRefresh = false }) {
    try {
      commit('SET_LOADING', true)
      const response = await request.getCustomerRequestsById(id, params, forceRefresh)
      commit('SET_REQUESTS', response.data)
      commit('SET_PAGINATION', response.pagination)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async acceptRequest({ commit }, { id }) {
    try {
      commit('SET_LOADING', true)
      const response = await request.accept(id)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async completeRequest({ commit }, { id, data }) {
    try {
      commit('SET_LOADING', true)
      const response = await request.complete(id, data)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  async reportReview({ commit }, { id, data }) {
    try {
      commit('SET_LOADING', true)
      const response = await request.report(id, data)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async cancelRequest({ commit }, { id }) {
    try {
      commit('SET_LOADING', true)
      const response = await request.cancel(id)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async submitReview({ commit }, { id, data }) {
    try {
      commit('SET_LOADING', true)
      const response = await request.submitReview(id, data)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateRequest({ commit }, { id, data }) {
    try {
      commit('SET_LOADING', true)
      const response = await request.update(id, data)
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
  SET_REQUESTS(state, requests) {
    state.requests = requests
  },

  SET_SELECTED_REQUEST(state, request) {
    state.selectedRequest = request
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

  ADD_REQUEST(state, request) {
    state.requests.unshift(request)
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
