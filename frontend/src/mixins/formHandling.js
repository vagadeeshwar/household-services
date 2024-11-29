import { ref, computed } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import _ from 'lodash'

export function useFormHandling(initialForm, validationRules) {
    const form = ref(_.cloneDeep(initialForm))
    const originalForm = ref(_.cloneDeep(initialForm))
    const v$ = useVuelidate(validationRules, form)
    const submitting = ref(false)

    const formIsDirty = computed(() => {
        return !_.isEqual(form.value, originalForm.value)
    })

    const resetForm = () => {
        form.value = _.cloneDeep(originalForm.value)
        v$.value.$reset()
    }

    const updateOriginalForm = () => {
        originalForm.value = _.cloneDeep(form.value)
    }

    const setFormData = (data) => {
        form.value = _.cloneDeep(data)
        originalForm.value = _.cloneDeep(data)
    }

    return {
        form,
        originalForm,
        v$,
        submitting,
        formIsDirty,
        resetForm,
        updateOriginalForm,
        setFormData
    }
}

export function useToastHandling() {
    const showSuccessToast = (message, title = 'Success') => {
        window.showToast({
            type: 'success',
            title,
            message
        })
    }

    const showErrorToast = (message, title = 'Error') => {
        window.showToast({
            type: 'danger',
            title,
            message: message || 'An unexpected error occurred'
        })
    }

    const showWarningToast = (message, title = 'Warning') => {
        window.showToast({
            type: 'warning',
            title,
            message
        })
    }

    const showInfoToast = (message, title = 'Information') => {
        window.showToast({
            type: 'info',
            title,
            message
        })
    }

    return {
        showSuccessToast,
        showErrorToast,
        showWarningToast,
        showInfoToast
    }
}

export function useModalHandling(modalId) {
    const modal = ref(null)

    const showModal = () => {
        if (!modal.value) {
            modal.value = new bootstrap.Modal(document.getElementById(modalId))
        }
        modal.value.show()
    }

    const hideModal = () => {
        if (modal.value) {
            modal.value.hide()
        }
    }

    return {
        showModal,
        hideModal
    }
}

export function useAsyncHandler() {
    const loading = ref(false)
    const error = ref(null)

    const handleAsync = async (asyncFn, {
        successMessage,
        errorMessage = 'An error occurred',
        showSuccess = true,
        showError = true,
        onSuccess = () => { },
        onError = () => { },
        onFinally = () => { }
    } = {}) => {
        try {
            loading.value = true
            error.value = null
            const result = await asyncFn()

            if (showSuccess && successMessage) {
                window.showToast({
                    type: 'success',
                    title: 'Success',
                    message: successMessage
                })
            }

            await onSuccess(result)
            return result
        } catch (err) {
            error.value = err.response?.data?.message || errorMessage

            if (showError) {
                window.showToast({
                    type: 'danger',
                    title: 'Error',
                    message: error.value
                })
            }

            await onError(err)
            throw err
        } finally {
            loading.value = false
            await onFinally()
        }
    }

    return {
        loading,
        error,
        handleAsync
    }
}

export function useFileHandling(validations = {}) {
    const file = ref(null)
    const fileError = ref(null)
    const preview = ref(null)

    const handleFileChange = (event) => {
        const selectedFile = event.target.files[0]
        fileError.value = null

        if (!selectedFile) {
            file.value = null
            preview.value = null
            return
        }

        // Size validation
        if (validations.maxSize && selectedFile.size > validations.maxSize) {
            fileError.value = `File size must not exceed ${validations.maxSize / (1024 * 1024)}MB`
            event.target.value = ''
            return
        }

        // Type validation
        if (validations.allowedTypes && !validations.allowedTypes.includes(selectedFile.type)) {
            fileError.value = `File type must be: ${validations.allowedTypes.join(', ')}`
            event.target.value = ''
            return
        }

        file.value = selectedFile

        // Generate preview for images
        if (selectedFile.type.startsWith('image/')) {
            const reader = new FileReader()
            reader.onload = (e) => {
                preview.value = e.target.result
            }
            reader.readAsDataURL(selectedFile)
        } else {
            preview.value = null
        }
    }

    const clearFile = () => {
        file.value = null
        preview.value = null
        fileError.value = null
    }

    return {
        file,
        fileError,
        preview,
        handleFileChange,
        clearFile
    }
}
