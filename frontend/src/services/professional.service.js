import cachedApi from '@/services/cachedApi'
class Professional {
  async getAll(params = {}) {
    return cachedApi.getPaginated('professionals', {
      ...params,
      service_type: params.serviceType,
    })
  }

  async getById(id) {
    return await cachedApi.getById(`professionals/${id}`)
  }

  async verify(id) {
    return await cachedApi.post(`professionals/${id}/verify`)
  }

  async block(id, reason) {
    return await cachedApi.post(`professionals/${id}/block`, { reason })
  }

  async getReviews(params = {}) {
    return cachedApi.getPaginated('professionals/reviews', {
      ...params,
      sort_by: params.sortBy,
      sort_order: params.sortOrder,
    })
  }

  async updateDocument(document) {
    return cachedApi.uploadFile('professionals/document', document, 'verification_document', 'PUT')
  }

  async updateService(serviceTypeId) {
    return await cachedApi.put('professionals/service', {
      service_type_id: serviceTypeId,
    })
  }
}

export const professional = new Professional()
