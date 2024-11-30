// frontend/src/store/modules/auth.js
import axios from 'axios'

const state = {
  token: localStorage.getItem('token') || null,
  user: JSON.parse(localStorage.getItem('user')) || null,
}

const getters = {
  isLoggedIn: state => !!state.token,
  userName: state => state.user ? state.user.full_name : '',
  userRole: state => state.user ? state.user.role : null,
  getToken: state => state.token,
  getUser: state => state.user,
}

const actions = {
  async login({ commit }, credentials) {
    try {
      const response = await axios.post('/api/login', credentials)
      const { token } = response.data.data

      // Get user profile
      const userResponse = await axios.get('/api/profile', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const user = userResponse.data.data

      // Save to store and localStorage
      commit('setToken', token)
      commit('setUser', user)

      // Set default auth header
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

      return Promise.resolve(user)
    } catch (error) {
      commit('clearAuth')
      return Promise.reject(error.response.data)
    }
  },

  async register({ commit }, { role, data }) {
    try {
      const endpoint = `/api/register/${role}`
      const response = await axios.post(endpoint, data)
      return Promise.resolve(response.data)
    } catch (error) {
      return Promise.reject(error.response.data)
    }
  },

  async logout({ commit }) {
    commit('clearAuth')
    delete axios.defaults.headers.common['Authorization']
    return Promise.resolve()
  },

  async updateProfile({ commit }, profileData) {
    try {
      const response = await axios.put('/api/profile', profileData)
      const updatedUser = response.data.data
      commit('setUser', updatedUser)
      return Promise.resolve(updatedUser)
    } catch (error) {
      return Promise.reject(error.response.data)
    }
  },

  async changePassword({ commit }, passwordData) {
    try {
      const response = await axios.post('/api/change-password', passwordData)
      return Promise.resolve(response.data)
    } catch (error) {
      return Promise.reject(error.response.data)
    }
  }
}

const mutations = {
  setToken(state, token) {
    state.token = token
    localStorage.setItem('token', token)
  },

  setUser(state, user) {
    state.user = user
    localStorage.setItem('user', JSON.stringify(user))
  },

  clearAuth(state) {
    state.token = null
    state.user = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}