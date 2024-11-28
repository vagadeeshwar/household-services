// frontend/src/App.vue
<template>
  <base-layout />
</template>

<script>
import BaseLayout from './layouts/BaseLayout.vue'

export default {
  name: 'App',
  components: {
    BaseLayout
  }
}
</script>

<style>
/* Global styles */
body {
  margin: 0;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", "Noto Sans", "Liberation Sans", Arial, sans-serif;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Bootstrap overrides and customizations */
.btn {
  font-weight: 500;
}

.form-control:focus {
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.15);
}

.invalid-feedback {
  font-size: 0.875em;
}
</style>