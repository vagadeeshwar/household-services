import { ref, computed } from 'vue'
import { useAsyncHandler, useFileHandling } from '@/mixins/formHandling'
import { documentValidationRules } from '@/utils/validation/profile'
import { profileService } from '@/services/profile.service'

export function useProfessionalProfile() {
    // File handling setup
    const {
        file: verificationDoc,
        fileError: docError,
        handleFileChange: handleDocChange,
        clearFile: clearDoc
    } = useFileHandling({
        maxSize: documentValidationRules.maxSize,
        allowedTypes: documentValidationRules.allowedTypes
    })

    const { handleAsync } = useAsyncHandler()

    // Check if professional has active requests
    const hasActiveRequests = ref(false)
    const checkActiveRequests = async () => {
        await handleAsync(
            async () => {
                const response = await profileService.getActiveRequests()
                hasActiveRequests.value = response.data.count > 0
            },
            {
                showError: false
            }
        )
    }

    // Update verification document
    const updateDocument = async () => {
        if (!verificationDoc.value) return

        const formData = new FormData()
        formData.append('verification_document', verificationDoc.value)

        await handleAsync(
            async () => {
                await profileService.updateDocument(formData)
                clearDoc()
            },
            {
                successMessage: 'Document uploaded successfully. Your profile will be reviewed.',
                errorMessage: 'Failed to upload document'
            }
        )
    }

    // Update service type
    const updateServiceType = async (serviceTypeId) => {
        await handleAsync(
            async () => {
                await profileService.updateServiceType(serviceTypeId)
            },
            {
                successMessage: 'Service type updated successfully. Your profile will be reviewed.',
                errorMessage: 'Failed to update service type'
            }
        )
    }

    // View document
    const viewDocument = (documentUrl) => {
        window.open(`/api/static/uploads/verification_docs/${documentUrl}`, '_blank')
    }

    return {
        verificationDoc,
        docError,
        hasActiveRequests,
        handleDocChange,
        updateDocument,
        updateServiceType,
        viewDocument,
        checkActiveRequests
    }
}