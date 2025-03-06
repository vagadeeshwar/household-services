import cachedApi from '@/services/cachedApi'
import api from '@/services/api'

class Professional {
  async getAll(params = {}, forceRefresh = false) {
    return cachedApi.getPaginated('professionals', params, { forceRefresh })
  }

  async getById(id, forceRefresh = false) {
    return await cachedApi.getById(`professionals/${id}`, { forceRefresh })
  }

  async verify(id) {
    const response = await api.post(`professionals/${id}/verify`)
    return response.data
  }

  async block(id, params = {}) {
    const response = await cachedApi.post(`professionals/${id}/block`, params)
    return response.data
  }

  async getReviews(params = {}, forceRefresh = false) {
    return cachedApi.getPaginated('professionals/reviews', params, { forceRefresh })
  }

  async updateDocument(params = {}) {
    const response = await api.uploadFile('professionals/document', params)
    return response.data
  }

  async updateService(params = {}) {
    const response = await api.put('professionals/service', {
      params,
    })
    return response.data
  }
}

export const professional = new Professional()
