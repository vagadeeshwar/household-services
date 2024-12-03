import api from './api'

class Service {
  async getAll(params = {}) {
    try {
      const response = await api.get('services', {
        params: {
          page: params.page,
          per_page: params.perPage,
          is_active: params.isActive,
        },
      })
      return response.data
    } catch (error) {
      console.error('Service API error:', error)
      throw error
    }
  }

  async getById(id) {
    const response = await api.get(`services/${id}`)
    return response.data
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
