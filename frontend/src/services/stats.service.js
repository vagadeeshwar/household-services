import cachedApi from '@/services/cachedApi'

class Stats {
  async getActivityLogs(params = {}, forceRefresh = false) {
    return await cachedApi.getPaginated('activity-logs', params, { forceRefresh })
  }
  async getOthersActivityLogs(params = {}, id, forceRefresh = false) {
    return await cachedApi.getPaginated(`activity-logs/${id}`, params, { forceRefresh })
  }
}

export const stats = new Stats()
