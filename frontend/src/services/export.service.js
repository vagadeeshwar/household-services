import api from './api'

class Export {
  async getStatus(id) {
    const response = await api.get(`exports/status/${id}`)
    return response.data
  }

  async generateServiceReport(params = {}) {
    const response = await api.post('exports/service-requests', {
      professional_id: params.professionalId,
      start_date: params.startDate,
      end_date: params.endDate,
    })
    return response.data
  }

  async download(filename) {
    const response = await api.get(`exports/download/${filename}`, {
      responseType: 'blob',
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)

    return true
  }

  async pollExportStatus(id, options = {}) {
    const {
      interval = 5000,
      timeout = 300000, // 5 minutes
      onProgress,
    } = options

    return new Promise((resolve, reject) => {
      const startTime = Date.now()
      const timer = setInterval(async () => {
        try {
          const status = await this.getStatus(id)

          if (onProgress) {
            onProgress(status)
          }

          if (status.completed) {
            clearInterval(timer)
            resolve(status)
          }

          if (Date.now() - startTime > timeout) {
            clearInterval(timer)
            reject(new Error('Export operation timed out'))
          }
        } catch (error) {
          clearInterval(timer)
          reject(error)
        }
      }, interval)
    })
  }
}

export const exportService = new Export()
