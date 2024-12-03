import api from './api'

class Professional {
  async getAll(params = {}) {
    return api.getPaginated('professionals', {
      ...params,
      service_type: params.serviceType,
    })
  }

  async getById(id) {
    const response = await api.get(`professionals/${id}`)
    return response.data
  }

  async verify(id) {
    const response = await api.post(`professionals/${id}/verify`)
    return response.data
  }

  async block(id, reason) {
    const response = await api.post(`professionals/${id}/block`, { reason })
    return response.data
  }

  async getDashboard() {
    const response = await api.get('professionals/dashboard')
    return response.data
  }

  async getReviews(params = {}) {
    return api.getPaginated('professionals/reviews', {
      ...params,
      sort_by: params.sortBy,
      sort_order: params.sortOrder,
    })
  }

  async updateDocument(document) {
    return api.uploadFile('professionals/document', document, 'verification_document', 'PUT')
  }

  async updateService(serviceTypeId) {
    const response = await api.put('professionals/service', {
      service_type_id: serviceTypeId,
    })
    return response.data
  }
}

export const professional = new Professional()
