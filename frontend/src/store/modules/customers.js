import { customer } from '@/services'

const state = {
  customers: [],
  selectedCustomer: null,
  loading: false,
  error: null,
  pagination: {
    currentPage: 1,
    totalPages: 0,
    perPage: 10,
  },
}

const getters = {
  allCustomers: (state) => state.customers,
  selectedCustomer: (state) => state.selectedCustomer,
  isLoading: (state) => state.loading,
  error: (state) => state.error,
  pagination: (state) => state.pagination,
}

const actions = {
  async fetchCustomers({ commit }, params = {}) {
    try {
      commit('SET_LOADING', true)
      const response = await customer.getAll(params)
      commit('SET_CUSTOMERS', response.data)
      commit('SET_PAGINATION', response.pagination)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchCustomerById({ commit }, id) {
    try {
      commit('SET_LOADING', true)
      const response = await customer.getById(id)
      commit('SET_SELECTED_CUSTOMER', response)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async blockCustomer({ commit }, { id, reason }) {
    try {
      commit('SET_LOADING', true)
      const response = await customer.block(id, reason)
      commit('UPDATE_CUSTOMER', response)
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
  SET_CUSTOMERS(state, customers) {
    state.customers = customers
  },

  SET_SELECTED_CUSTOMER(state, customer) {
    state.selectedCustomer = customer
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

  UPDATE_CUSTOMER(state, updatedCustomer) {
    const index = state.customers.findIndex((c) => c.id === updatedCustomer.id)
    if (index !== -1) {
      state.customers.splice(index, 1, updatedCustomer)
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
