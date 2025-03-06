import cachedApi from '@/services/cachedApi'
import api from '@/services/api'

class Customer {
  async getAll(params = {}) {
    return await cachedApi.getPaginated('customers', params)
  }

  async getById(id) {
    return await cachedApi.getById(`customers/${id}`)
  }

  async block(id, reason) {
    const response = await api.post(`customers/${id}/block`, { reason })
    return response.data
  }
}

export const customer = new Customer()
