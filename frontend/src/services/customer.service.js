import api from './api'

class Customer {
  async getAll(params = {}) {
    return api.getPaginated('customers', params)
  }

  async getById(id) {
    const response = await api.get(`customers/${id}`)
    return response.data
  }

  async block(id, reason) {
    const response = await api.post(`customers/${id}/block`, { reason })
    return response.data
  }
}

export const customer = new Customer()
