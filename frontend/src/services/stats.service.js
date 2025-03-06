import cachedApi from '@/services/cachedApi'

class Stats {
  async getActivityLogs(params = {}) {
    return await cachedApi.getPaginated('activity-logs', {
      params: {
        action: params.action,
        page: params.page,
        per_page: params.perPage,
        start_date: params.startDate,
        end_date: params.endDate,
      },
    })
  }
  async getOthersActivityLogs(id, params = {}) {
    return await cachedApi.getPaginated(`activity-logs/${id}`, {
      params: {
        action: params.action,
        page: params.page,
        per_page: params.perPage,
        start_date: params.startDate,
        end_date: params.endDate,
      },
    })
  }
}

export const stats = new Stats()
