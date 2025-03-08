import { auth } from '@/services'

const state = {
  user: JSON.parse(localStorage.getItem('user')) || {
    id: null,
    username: '',
    email: '',
    full_name: '',
    phone: '',
    address: '',
    pin_code: '',
    role: '',
    is_active: false,
    created_at: null,
    last_login: null,
    verification_documents: null,
    // Add default values for all user properties used in your app (will be used while the api response is being fetched)
  },
  token: localStorage.getItem('access_token'),
  loading: false,
  error: null,
}

const getters = {
  isLoggedIn: (state) => !!state.token && !!state.user,
  userRole: (state) => state.user?.role,
  userName: (state) => state.user?.full_name,
  userEmail: (state) => state.user?.email,
  currentUser: (state) => state.user,
  token: (state) => state.token,
  isLoading: (state) => state.loading,
  error: (state) => state.error,
}

const actions = {
  async login({ commit }, { data }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)

    try {
      const loginResponse = await auth.login(data)

      if (!loginResponse?.data?.token) {
        throw new Error('Invalid login response')
      }

      commit('SET_TOKEN', loginResponse.data.token)

      const profileResponse = await auth.getProfile()

      if (!profileResponse?.data) {
        throw new Error('Invalid profile response')
      }

      commit('SET_USER', profileResponse.data)
      return profileResponse.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Login failed')
      commit('CLEAR_AUTH')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async registerCustomer({ commit }, { data }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)

    try {
      const response = await auth.registerCustomer(data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Registration failed')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async registerProfessional({ commit }, { data }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)

    try {
      const response = await auth.registerProfessional(data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Registration failed')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  async getProfile({ commit }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)

    try {
      const response = await auth.getProfile()
      commit('SET_USER', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Profile fetch failed')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateProfile({ commit }, { data }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)

    try {
      const response = await auth.updateProfile(data)
      commit('SET_USER', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Profile update failed')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async changePassword({ commit }, { data }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)

    try {
      const response = await auth.changePassword(data)
      commit('CLEAR_AUTH')
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Password change failed')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async deleteAccount({ commit }, { data }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)

    try {
      const response = await auth.deleteAccount(data)
      commit('CLEAR_AUTH')
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Account deletion failed')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  logout({ commit, dispatch }) {
    commit('CLEAR_AUTH')
    dispatch('apiCache/clearAllCache', null, { root: true })
  },
}

const mutations = {
  SET_TOKEN(state, token) {
    state.token = token
    localStorage.setItem('access_token', token)
  },

  SET_USER(state, user) {
    state.user = user
    localStorage.setItem('user', JSON.stringify(user))
  },

  SET_LOADING(state, loading) {
    state.loading = loading
  },

  SET_ERROR(state, error) {
    state.error = error
  },

  CLEAR_AUTH(state) {
    state.token = null
    state.user = null
    state.error = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
