import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { useFormHandling, useAsyncHandler, useToastHandling } from '@/mixins/formHandling'
import { profileValidationRules, passwordValidationRules } from '@/utils/validation/profile'
import { profileService } from '@/services/profile.service'

export function useProfileManagement(userId = null) {
    const store = useStore()
    const router = useRouter()
    const isOwnProfile = computed(() => !userId || userId === store.getters['auth/userId'])

    // Form handling setup
    const { form, v$, formIsDirty, submitting, resetForm, updateOriginalForm } = useFormHandling({
        // Initial form shape
        email: '',
        full_name: '',
        phone: '',
        pin_code: '',
        address: '',
        description: '',
        service_type_id: '',
        experience_years: ''
    }, profileValidationRules)

    // Password form handling
    const passwordForm = ref({
        old_password: '',
        new_password: '',
        confirm_password: ''
    })

    const { handleAsync } = useAsyncHandler()
    const { showSuccessToast, showErrorToast } = useToastHandling()

    // Fetch profile data
    const fetchProfile = async () => {
        await handleAsync(
            async () => {
                const response = await profileService.getProfile(userId)
                form.value = { ...response.data }
                updateOriginalForm()
            },
            {
                errorMessage: 'Failed to load profile'
            }
        )
    }

    // Update profile
    const updateProfile = async () => {
        const isValid = await v$.value.$validate()
        if (!isValid) return

        await handleAsync(
            async () => {
                const response = await profileService.updateProfile(form.value)
                updateOriginalForm()
                return response
            },
            {
                successMessage: 'Profile updated successfully',
                errorMessage: 'Failed to update profile'
            }
        )
    }

    // Change password
    const changePassword = async () => {
        if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
            showErrorToast('Passwords do not match')
            return
        }

        await handleAsync(
            async () => {
                await profileService.changePassword({
                    old_password: passwordForm.value.old_password,
                    new_password: passwordForm.value.new_password
                })
                passwordForm.value = {
                    old_password: '',
                    new_password: '',
                    confirm_password: ''
                }
            },
            {
                successMessage: 'Password changed successfully',
                errorMessage: 'Failed to change password'
            }
        )
    }

    // Delete account
    const deleteAccount = async (password) => {
        await handleAsync(
            async () => {
                await profileService.deleteAccount(password)
                await store.dispatch('auth/logout')
                router.push('/login')
            },
            {
                successMessage: 'Account deleted successfully',
                errorMessage: 'Failed to delete account'
            }
        )
    }

    return {
        form,
        v$,
        formIsDirty,
        submitting,
        passwordForm,
        isOwnProfile,
        fetchProfile,
        updateProfile,
        changePassword,
        deleteAccount,
        resetForm
    }
}