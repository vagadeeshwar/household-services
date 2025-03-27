import api from '@/services/api'
import cachedApi from '@/services/cachedApi'

class Request {
  async create(data) {
    const response = await api.post('requests', data)
    return response.data
  }

  async getProfessionalRequests(params = {}, forceRefresh = false) {
    return cachedApi.getPaginated('professionals/requests', params, { forceRefresh })
  }

  async getProfessionalRequestsById(id, params = {}, forceRefresh = false) {
    return cachedApi.getPaginated(`professionals/${id}/requests`, params, { forceRefresh })
  }

  async getCustomerRequests(params = {}, forceRefresh = false) {
    return cachedApi.getPaginated('customers/requests', params, { forceRefresh })
  }

  async getCustomerRequestsById(id, params = {}, forceRefresh = false) {
    return cachedApi.getPaginated(`customers/${id}/requests`, params, { forceRefresh })
  }

  async accept(id) {
    const response = await api.post(`requests/${id}/accept`)
    return response.data
  }

  async complete(id, data) {
    const response = await api.post(`requests/${id}/complete`, data)
    return response.data
  }

  async report(id, data) {
    const response = await api.post(`reviews/${id}/report`, data)
    return response.data
  }

  async cancel(id) {
    const response = await api.post(`requests/${id}/cancel`)
    return response.data
  }

  async submitReview(id, data) {
    const response = await api.post(`requests/${id}/review`, data)
    return response.data
  }

  async update(id, params = {}) {
    const response = await api.put(`requests/${id}`, params)
    return response.data
  }
}

export const request = new Request()
