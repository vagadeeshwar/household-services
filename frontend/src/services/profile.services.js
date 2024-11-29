import axios from 'axios'

class ProfileService {
    async getProfile(userId = null) {
        const url = userId ? `/api/users/${userId}` : '/api/profile'
        const response = await axios.get(url)
        return response.data
    }

    async updateProfile(profileData) {
        const response = await axios.put('/api/profile', profileData)
        return response.data
    }

    async changePassword(passwordData) {
        const response = await axios.post('/api/change-password', passwordData)
        return response.data
    }

    async updateDocument(formData) {
        const response = await axios.put('/api/professionals/document', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
        return response.data
    }

    async deleteAccount(password) {
        const response = await axios.delete('/api/delete-account', {
            data: { password }
        })
        return response.data
    }

    async updateServiceType(serviceTypeId) {
        const response = await axios.put('/api/professionals/service', {
            service_type_id: serviceTypeId
        })
        return response.data
    }

    // Helper method to validate file before upload
    validateFile(file) {
        const maxSize = 5 * 1024 * 1024 // 5MB
        const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf']

        if (!file) return { valid: false, error: 'No file selected' }
        if (!allowedTypes.includes(file.type)) {
            return { valid: false, error: 'Invalid file type. Please upload a PDF, JPG, or PNG file' }
        }
        if (file.size > maxSize) {
            return { valid: false, error: 'File size exceeds 5MB limit' }
        }

        return { valid: true }
    }
}

export const profileService = new ProfileService()