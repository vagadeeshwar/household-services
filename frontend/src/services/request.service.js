import api from '@/services/api'
import cachedApi from '@/services/cachedApi'

class Request {
  async create(data) {
    const response = await api.post('requests', {
      service_id: data.serviceId,
      preferred_time: data.preferredTime,
      description: data.description,
    })
    return response.data
  }

  async getAll(params = {}) {
    return await cachedApi.getPaginated('requests', {
      ...params,
      service_id: params.serviceId,
      professional_id: params.professionalId,
      customer_id: params.customerId,
    })
  }

  async getById(id) {
    return await cachedApi.getById(`requests/${id}`)
  }

  async getProfessionalRequests(params = {}) {
    return cachedApi.getPaginated('professional/requests', params)
  }

  async getCustomerRequests(params = {}) {
    return cachedApi.getPaginated('customer/requests', params)
  }

  async accept(id) {
    const response = await api.post(`requests/${id}/accept`)
    return response.data
  }

  async complete(id, remarks) {
    const response = await api.post(`requests/${id}/complete`, { remarks })
    return response.data
  }

  async cancel(id) {
    const response = await api.post(`requests/${id}/cancel`)
    return response.data
  }

  async submitReview(id, data) {
    const response = await api.post(`requests/${id}/review`, {
      rating: data.rating,
      comment: data.comment,
    })
    return response.data
  }

  async update(id, data) {
    const payload = {
      ...(data.preferredTime && { preferred_time: data.preferredTime }),
      ...(data.description && { description: data.description }),
    }
    const response = await api.put(`requests/${id}`, payload)
    return response.data
  }
}

export const request = new Request()
