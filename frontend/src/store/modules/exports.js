import { exportService } from '@/services'

const state = {
  currentExport: null,
  exports: [], // Track multiple exports if needed
  loading: {
    status: false,
    generate: false,
    download: false,
  },
  error: null,
}

const getters = {
  currentExport: (state) => state.currentExport,
  isLoading: (state) => Object.values(state.loading).some((status) => status),
  error: (state) => state.error,
  allExports: (state) => state.exports,
}

const actions = {
  async checkExportStatus({ commit }, { id }) {
    try {
      commit('SET_LOADING', { type: 'status', value: true })
      const response = await exportService.getStatus(id)
      commit('SET_CURRENT_EXPORT', response)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', { type: 'status', value: false })
    }
  },

  async generateServiceReport({ commit }, { data }) {
    try {
      commit('SET_LOADING', { type: 'generate', value: true })
      const response = await exportService.generateServiceReport(data)
      commit('SET_CURRENT_EXPORT', response)
      commit('ADD_EXPORT', response)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', { type: 'generate', value: false })
    }
  },

  async downloadReport({ commit }, { data }) {
    try {
      commit('SET_LOADING', { type: 'download', value: true })
      const response = await exportService.download(data)
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', { type: 'download', value: false })
    }
  },

  async pollExportStatus({ commit }, { id, options = {} }) {
    try {
      const response = await exportService.pollExportStatus(id, {
        ...options,
        onProgress: (status) => {
          commit('UPDATE_EXPORT_STATUS', { id, status })
        },
      })
      return response
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    }
  },

  clearCurrentExport({ commit }) {
    commit('SET_CURRENT_EXPORT', null)
  },
}

const mutations = {
  SET_CURRENT_EXPORT(state, exportData) {
    state.currentExport = exportData
  },

  SET_LOADING(state, { type, value }) {
    state.loading[type] = value
  },

  SET_ERROR(state, error) {
    state.error = error
  },

  ADD_EXPORT(state, exportData) {
    state.exports.unshift(exportData)
  },

  UPDATE_EXPORT_STATUS(state, { id, status }) {
    // Update in exports array
    const exportIndex = state.exports.findIndex((exp) => exp.id === id)
    if (exportIndex !== -1) {
      state.exports[exportIndex] = { ...state.exports[exportIndex], ...status }
    }

    // Update current export if it matches
    if (state.currentExport?.id === id) {
      state.currentExport = { ...state.currentExport, ...status }
    }
  },

  RESET_STATE(state) {
    state.currentExport = null
    state.exports = []
    state.error = null
    state.loading = {
      status: false,
      generate: false,
      download: false,
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
