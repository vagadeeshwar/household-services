import cachedApi from '@/services/cachedApi'
import api from '@/services/api'

class Service {
  async getAll(params = {}, forceRefresh = false) {
    return await cachedApi.getPaginated('services/all', params, { forceRefresh })
  }

  async getActive(params = {}, forceRefresh = false) {
    return await cachedApi.getPaginated('services', params, { forceRefresh })
  }

  async getActiveById(id, params = {}, forceRefresh = false) {
    return await cachedApi.getById(`services/${id}`, params, { forceRefresh })
  }

  async getAllById(id, params = {}, forceRefresh = false) {
    return await cachedApi.getById(`services/all/${id}`, params, { forceRefresh })
  }

  async create(params = {}) {
    const response = await api.post('services', params)

    cachedApi.invalidateCache('services')
    cachedApi.invalidateCache('services/all')
    return response.data
  }

  async update(id, params = {}) {
    const response = await api.put(`services/${id}`, params)

    cachedApi.invalidateCache('services')
    cachedApi.invalidateCache('services/all')
    cachedApi.invalidateCache(`services/${id}`)
    cachedApi.invalidateCache(`services/all/${id}`)
    return response.data
  }

  async toggle(id, params = {}) {
    const response = await api.post(`services/${id}/toggle`, params)

    cachedApi.invalidateCache('services')
    cachedApi.invalidateCache('services/all')
    cachedApi.invalidateCache(`services/${id}`)
    cachedApi.invalidateCache(`services/all/${id}`)
    return response.data
  }

  async delete(id, params = {}) {
    const response = await api.delete(`services/${id}`, params)
    cachedApi.invalidateCache('services')
    cachedApi.invalidateCache('services/all')
    cachedApi.invalidateCache(`services/${id}`)
    cachedApi.invalidateCache(`services/all/${id}`)

    return response.data
  }
}

export const service = new Service()
