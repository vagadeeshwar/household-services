import cachedApi from '@/services/cachedApi'
import api from '@/services/api'

class Customer {
  async getAll(params = {}, forceRefresh = false) {
    return await cachedApi.getPaginated('customers', params, { forceRefresh })
  }

  async getById(id, forceRefresh = false) {
    return await cachedApi.getById(`customers/${id}`, { forceRefresh })
  }

  async block(id, reason) {
    const response = await api.post(`customers/${id}/block`, { reason })
    return response.data
  }
}

export const customer = new Customer()
