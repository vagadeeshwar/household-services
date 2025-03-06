import api from '@/services/api'
import cachedApi from '@/services/cachedApi'

class Request {
  async create(params = {}) {
    const response = await api.post('requests', params)
    return response.data
  }

  async getAll(params = {}, forceRefresh = false) {
    return await cachedApi.getPaginated('requests', params, { forceRefresh })
  }

  async getById(id, params, forceRefresh = false) {
    return await cachedApi.getById(`requests/${id}`, params, { forceRefresh })
  }

  async getProfessionalRequests(params = {}, forceRefresh = false) {
    return cachedApi.getPaginated('professional/requests', params, { forceRefresh })
  }

  async getCustomerRequests(params = {}, forceRefresh = false) {
    return cachedApi.getPaginated('customer/requests', params, { forceRefresh })
  }

  async accept(id, params = {}) {
    const response = await api.post(`requests/${id}/accept`, params)
    return response.data
  }

  async complete(id, params = {}) {
    const response = await api.post(`requests/${id}/complete`, params)
    return response.data
  }

  async cancel(id, params = {}) {
    const response = await api.post(`requests/${id}/cancel`, params)
    return response.data
  }

  async submitReview(id, params = {}) {
    const response = await api.post(`requests/${id}/review`, params)
    return response.data
  }

  async update(id, params = {}) {
    const response = await api.put(`requests/${id}`, params)
    return response.data
  }
}

export const request = new Request()
