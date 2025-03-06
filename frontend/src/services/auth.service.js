import api from './api'

class AuthService {
  async login(credentials) {
    const response = await api.post('/login', credentials, {
      headers: {
        'Content-Type': 'application/json',
      },
    })
    return response.data
  }

  async getProfile() {
    const response = await api.get('/profile')
    return response.data
  }

  async registerCustomer(data) {
    const response = await api.post('/register/customer', {
      username: data.username,
      email: data.email,
      password: data.password,
      full_name: data.fullName,
      phone: data.phone,
      address: data.address,
      pin_code: data.pinCode,
    })
    return response.data
  }

  async registerProfessional(formData) {
    const headers = {
      'Content-Type': 'multipart/form-data',
    }
    const response = await api.post('/register/professional', formData, { headers })
    return response.data
  }

  async updateProfile(data) {
    const response = await api.put('/profile', {
      email: data.email,
      full_name: data.fullName,
      phone: data.phone,
      address: data.address,
      pin_code: data.pinCode,
      ...(data.description && { description: data.description }),
    })
    return response.data
  }

  async changePassword(oldPassword, newPassword) {
    const response = await api.post('/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    })
    return response.data
  }

  async deleteAccount(password) {
    const response = await api.delete('/delete-account', {
      password: { password },
    })
    return response.data
  }
}

export const auth = new AuthService()
