import api from './api'
import cachedApi from './cachedApi'

class AuthService {
  async login(data) {
    const response = await api.post('/login', data)
    return response.data
  }

  async getProfile() {
    return await cachedApi.get('/profile')
  }

  async registerCustomer(data) {
    const response = await api.post('/register/customer', data)
    return response.data
  }

  async registerProfessional(data) {
    const headers = {
      'Content-Type': 'multipart/form-data',
    }
    const response = await api.post('/register/professional', data, { headers })
    return response.data
  }

  async updateProfile(data) {
    const response = await api.put('/profile', data)
    return response.data
  }

  async changePassword(data) {
    const response = await api.post('/change-password', data)
    return response.data
  }

  async deleteAccount(data) {
    const response = await api.delete('/delete-account', { data: data })
    return response.data
  }

  async getDashboard(params = {}, forceRefresh = false) {
    return cachedApi.getPaginated('admin/dashboard', params, { forceRefresh })
  }
}

export const auth = new AuthService()
