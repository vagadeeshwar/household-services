import api from './api'

class Public {
  async submitContact(data) {
    const response = await api.post('contact', {
      name: data.name,
      email: data.email,
      subject: data.subject,
      message: data.message,
    })
    return response.data
  }
}

export const publicService = new Public()
