# src/components/shared/Loading.vue
<template>
    <div class="loading-container" :class="{ overlay: overlay, full: fullscreen }">
        <div class="loading-content">
            <div class="spinner-border text-primary" :class="spinnerSize" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p v-if="message" class="mt-2 mb-0 text-muted">{{ message }}</p>
        </div>
    </div>
</template>

<script>
export default {
    name: 'Loading',
    props: {
        message: {
            type: String,
            default: ''
        },
        overlay: {
            type: Boolean,
            default: false
        },
        fullscreen: {
            type: Boolean,
            default: false
        },
        size: {
            type: String,
            default: 'md',
            validator: value => ['sm', 'md', 'lg'].includes(value)
        }
    },
    computed: {
        spinnerSize() {
            return {
                'spinner-border-sm': this.size === 'sm',
                '': this.size === 'md',
                'spinner-border-lg': this.size === 'lg'
            }
        }
    }
}
</script>

<style scoped>
.loading-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 200px;
}

.loading-container.overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.8);
    z-index: 1000;
}

.loading-container.full {
    position: fixed;
    width: 100vw;
    height: 100vh;
}

.loading-content {
    text-align: center;
}

.spinner-border-lg {
    width: 3rem;
    height: 3rem;
}
</style>