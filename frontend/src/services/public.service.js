import api from '@/services/api'

class Public {
  async submitContact(params = {}) {
    const response = await api.post('contact', params)
    return response.data
  }
}

export const publicService = new Public()
