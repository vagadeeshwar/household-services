import api from './api'

class Stats {
  async getDashboard() {
    const response = await api.get('dashboard-stats')
    return response.data
  }

  async getDetailed(params = {}) {
    const response = await api.get('detailed-stats', {
      params: {
        stat_type: params.type,
        page: params.page,
        per_page: params.perPage,
      },
    })
    return response.data
  }
}

export const stats = new Stats()
