import cachedApi from '@/services/cachedApi'
import api from '@/services/api'

class Service {
  async getAll(params = {}) {
    try {
      return await cachedApi.getPaginated('services/all', {
        params: {
          page: params.page,
          per_page: params.perPage,
        },
      })
    } catch (error) {
      console.error('Service API error:', error)
      throw error
    }
  }

  async getActive(params = {}) {
    try {
      return await cachedApi.getPaginated('services', {
        params: {
          page: params.page,
          per_page: params.perPage,
        },
      })
    } catch (error) {
      console.error('Service API error:', error)
      throw error
    }
  }

  async getActiveById(id) {
    return await cachedApi.getById(`services/${id}`)
  }

  async getAllById(id) {
    return await cachedApi.getById(`services/all/${id}`)
  }

  async create(data) {
    const response = await api.post('services', {
      name: data.name,
      description: data.description,
      base_price: data.basePrice,
      estimated_time: data.estimatedTime,
    })
    return response.data
  }

  async update(id, data) {
    const payload = {
      ...(data.name && { name: data.name }),
      ...(data.description && { description: data.description }),
      ...(data.basePrice && { base_price: data.basePrice }),
      ...(data.estimatedTime && { estimated_time: data.estimatedTime }),
    }
    const response = await api.put(`services/${id}`, payload)
    return response.data
  }

  async toggle(id) {
    const response = await api.post(`services/${id}/toggle`)
    return response.data
  }

  async delete(id) {
    const response = await api.delete(`services/${id}`)
    return response.data
  }
}

export const service = new Service()
