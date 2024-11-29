# src/components/shared/FormNavigationGuard.vue
<template>
    <ConfirmDialog id="navigationConfirmDialog" title="Unsaved Changes"
        message="You have unsaved changes. Are you sure you want to leave?" type="warning" confirm-text="Leave"
        cancel-text="Stay" @confirm="handleConfirm" />
</template>

<script>
import { ref, watch, onBeforeMount, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { Modal } from 'bootstrap'
import ConfirmDialog from './ConfirmDialog.vue'

export default {
    name: 'FormNavigationGuard',
    components: {
        ConfirmDialog
    },

    props: {
        isDirty: {
            type: Boolean,
            required: true
        },
        confirmMessage: {
            type: String,
            default: 'You have unsaved changes. Are you sure you want to leave?'
        }
    },

    emits: ['proceed', 'cancel'],

    setup(props, { emit }) {
        const router = useRouter()
        const modal = ref(null)
        let nextRoute = null
        let unregisterGuard = null

        const showConfirmDialog = () => {
            if (!modal.value) {
                modal.value = new Modal(document.getElementById('navigationConfirmDialog'))
            }
            modal.value.show()
        }

        const handleConfirm = () => {
            emit('proceed')
            if (nextRoute) {
                router.push(nextRoute)
            }
        }

        // Router navigation guard
        const navigationGuard = (to, from, next) => {
            if (props.isDirty) {
                nextRoute = to
                showConfirmDialog()
                next(false)
            } else {
                next()
            }
        }

        // Window beforeunload handler
        const beforeUnloadHandler = (e) => {
            if (props.isDirty) {
                e.preventDefault()
                e.returnValue = ''
            }
        }

        // Setup guards when component mounts
        onBeforeMount(() => {
            unregisterGuard = router.beforeEach(navigationGuard)
            window.addEventListener('beforeunload', beforeUnloadHandler)
        })

        // Cleanup when component unmounts
        onBeforeUnmount(() => {
            if (unregisterGuard) unregisterGuard()
            window.removeEventListener('beforeunload', beforeUnloadHandler)
        })

        // Watch for changes in isDirty prop
        watch(() => props.isDirty, (newValue) => {
            if (!newValue && modal.value) {
                const modalInstance = Modal.getInstance(document.getElementById('navigationConfirmDialog'))
                if (modalInstance) modalInstance.hide()
            }
        })

        return {
            handleConfirm
        }
    }
}
</script>