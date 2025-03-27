import cachedApi from '@/services/cachedApi'
import api from '@/services/api'

class Customer {
  async getAll(params = {}, forceRefresh = false) {
    return await cachedApi.getPaginated('customers', params, { forceRefresh })
  }

  async getById(id, params = {}, forceRefresh = false) {
    return await cachedApi.getById(`customers/${id}`, params, { forceRefresh })
  }

  async block(id, data) {
    const response = await api.post(`customers/${id}/block`, data)
    return response.data
  }

  async unblock(id) {
    const response = await api.post(`customers/${id}/unblock`)
    return response.data
  }

  async getDashboard(params = {}, forceRefresh = false) {
    return cachedApi.getPaginated('customers/dashboard', params, { forceRefresh })
  }
}

export const customer = new Customer()
