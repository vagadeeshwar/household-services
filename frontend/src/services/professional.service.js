import cachedApi from '@/services/cachedApi'
import api from '@/services/api'

class Professional {
  async getAll(params = {}, forceRefresh = false) {
    return cachedApi.getPaginated('professionals', params, { forceRefresh })
  }

  async getById(id, params = {}, forceRefresh = false) {
    return await cachedApi.getById(`professionals/${id}`, params, { forceRefresh })
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

  async updateDocument(data) {
    const headers = {
      'Content-Type': 'multipart/form-data',
    }
    const response = await api.put('document', data, { headers })
    return response.data
  }

  async downloadDocument() {
    const response = await api.get('my-document', {
      responseType: 'blob',
    })
    return response
  }

  async updateService(params = {}) {
    const response = await api.put('professionals/service', {
      params,
    })
    return response.data
  }
}

export const professional = new Professional()
