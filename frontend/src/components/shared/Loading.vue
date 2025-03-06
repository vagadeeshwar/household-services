<template>
  <div v-if="show" class="loading-container" :class="{ overlay: overlay, full: fullscreen }">
    <div class="loading-content">
      <div class="spinner-border" :class="spinnerClass" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p v-if="message" class="mt-2 mb-0 text-muted">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  message: { type: String, default: '' },
  overlay: { type: Boolean, default: false },
  fullscreen: { type: Boolean, default: false },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value),
  },
})

const spinnerClass = computed(() => ({
  'spinner-border-sm': props.size === 'sm',
  'spinner-border-lg': props.size === 'lg',
}))
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
  inset: 0;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 1000;
}

.loading-container.full {
  position: fixed;
  width: 100vw;
  height: 100vh;
}
</style>
