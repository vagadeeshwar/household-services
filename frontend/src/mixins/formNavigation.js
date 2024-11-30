// src/mixins/formNavigation.js
import { ref } from 'vue'
import { useRouter, onBeforeRouteLeave } from 'vue-router'
import { Modal } from 'bootstrap'

export function useFormNavigation(isDirty, resetForm) {
    const router = useRouter()
    const navigationConfirmDialog = ref(null)
    let nextRoute = null

    onBeforeRouteLeave((to, from, next) => {
        if (isDirty.value) {
            nextRoute = to
            showConfirmDialog()
            next(false)
        } else {
            next()
        }
    })

    const showConfirmDialog = () => {
        if (!navigationConfirmDialog.value) {
            navigationConfirmDialog.value = new Modal(document.getElementById('navigationConfirmDialog'))
        }
        navigationConfirmDialog.value.show()
    }

    const handleNavigationConfirm = () => {
        resetForm()
        hideConfirmDialog()
        if (nextRoute) {
            router.push(nextRoute)
        }
    }

    const hideConfirmDialog = () => {
        const modalInstance = Modal.getInstance(document.getElementById('navigationConfirmDialog'))
        if (modalInstance) {
            modalInstance.hide()
            // Clean up the backdrop manually if it exists
            const backdrop = document.querySelector('.modal-backdrop')
            if (backdrop) {
                backdrop.remove()
            }
            // Reset body styles
            document.body.classList.remove('modal-open')
            document.body.style.removeProperty('padding-right')
        }
    }

    return {
        navigationConfirmDialog,
        showConfirmDialog,
        handleNavigationConfirm,
        hideConfirmDialog
    }
}