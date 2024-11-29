import axios from 'axios'

const state = {
    profile: null,
    loading: false,
    error: null
}

const getters = {
    profile: state => state.profile,
    isLoading: state => state.loading,
    error: state => state.error,
    isProfessional: state => state.profile?.role === 'professional',
    isCustomer: state => state.profile?.role === 'customer',
    isAdmin: state => state.profile?.role === 'admin',
    hasActiveRequests: state => {
        if (!state.profile || !state.profile.professional_profile) return false
        return state.profile.professional_profile.active_requests_count > 0
    }
}

const actions = {
    async fetchProfile({ commit }, userId = null) {
        try {
            commit('SET_LOADING', true)
            const url = userId ? `/api/users/${userId}` : '/api/profile'
            const response = await axios.get(url)
            commit('SET_PROFILE', response.data.data)
        } catch (error) {
            commit('SET_ERROR', error.response?.data?.message || 'Failed to fetch profile')
            throw error
        } finally {
            commit('SET_LOADING', false)
        }
    },

    async updateProfile({ commit }, profileData) {
        try {
            commit('SET_LOADING', true)
            const response = await axios.put('/api/profile', profileData)
            commit('SET_PROFILE', response.data.data)
            return response.data
        } catch (error) {
            commit('SET_ERROR', error.response?.data?.message || 'Failed to update profile')
            throw error
        } finally {
            commit('SET_LOADING', false)
        }
    },

    async changePassword({ commit }, passwordData) {
        try {
            commit('SET_LOADING', true)
            const response = await axios.post('/api/change-password', passwordData)
            return response.data
        } catch (error) {
            commit('SET_ERROR', error.response?.data?.message || 'Failed to change password')
            throw error
        } finally {
            commit('SET_LOADING', false)
        }
    },

    async updateDocument({ commit }, formData) {
        try {
            commit('SET_LOADING', true)
            const response = await axios.put('/api/professionals/document', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            })
            commit('SET_PROFILE', response.data.data)
            return response.data
        } catch (error) {
            commit('SET_ERROR', error.response?.data?.message || 'Failed to update document')
            throw error
        } finally {
            commit('SET_LOADING', false)
        }
    },

    async deleteAccount({ commit }, password) {
        try {
            commit('SET_LOADING', true)
            const response = await axios.delete('/api/delete-account', {
                data: { password }
            })
            commit('CLEAR_PROFILE')
            return response.data
        } catch (error) {
            commit('SET_ERROR', error.response?.data?.message || 'Failed to delete account')
            throw error
        } finally {
            commit('SET_LOADING', false)
        }
    },

    clearError({ commit }) {
        commit('SET_ERROR', null)
    }
}

const mutations = {
    SET_PROFILE(state, profile) {
        state.profile = profile
    },
    SET_LOADING(state, loading) {
        state.loading = loading
    },
    SET_ERROR(state, error) {
        state.error = error
    },
    CLEAR_PROFILE(state) {
        state.profile = null
    }
}

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
}