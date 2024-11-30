// src/components/shared/ConfirmDialog.vue
<template>
    <div class="modal fade" :id="id" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog" :class="{ 'modal-sm': size === 'sm', 'modal-lg': size === 'lg' }">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">{{ title }}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <slot name="body">
                        {{ message }}
                    </slot>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        {{ cancelText }}
                    </button>
                    <button type="button" :class="['btn', `btn-${type}`]" @click="handleConfirm">
                        <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                        {{ confirmText }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onUnmounted } from 'vue'
import { Modal } from 'bootstrap'

export default {
    name: 'ConfirmDialog',
    props: {
        id: {
            type: String,
            required: true
        },
        title: {
            type: String,
            default: 'Confirm Action'
        },
        message: {
            type: String,
            default: 'Are you sure you want to proceed?'
        },
        type: {
            type: String,
            default: 'primary',
            validator: value => ['primary', 'danger', 'warning', 'success'].includes(value)
        },
        confirmText: {
            type: String,
            default: 'Confirm'
        },
        cancelText: {
            type: String,
            default: 'Cancel'
        },
        size: {
            type: String,
            default: 'md',
            validator: value => ['sm', 'md', 'lg'].includes(value)
        }
    },

    emits: ['confirm', 'hidden.bs.modal'],

    setup(props, { emit }) {
        const loading = ref(false)
        let modalInstance = null

        const handleConfirm = async () => {
            try {
                loading.value = true
                await emit('confirm')
            } finally {
                loading.value = false
                hideModal()
            }
        }

        const hideModal = () => {
            if (!modalInstance) {
                modalInstance = Modal.getInstance(document.getElementById(props.id))
            }
            if (modalInstance) {
                modalInstance.hide()
            }
        }

        // Clean up when component is unmounted
        onUnmounted(() => {
            const backdrop = document.querySelector('.modal-backdrop')
            if (backdrop) {
                backdrop.remove()
            }
            document.body.classList.remove('modal-open')
            document.body.style.removeProperty('padding-right')
        })

        return {
            loading,
            handleConfirm
        }
    }
}
</script>