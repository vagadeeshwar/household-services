<template>
  <div class="layout-container">
    <TheNavbar />
    <main class="flex-grow-1">
      <router-view v-slot="{ Component }">
        <component :is="Component" />
      </router-view>
      <Toast />
    </main>
    <footer class="footer mt-auto py-4 bg-light">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-md-6 text-center text-md-start">
            <span class="text-muted">
              © {{ currentYear }} Household Services. All rights reserved.
            </span>
          </div>
          <div class="col-md-6">
            <ul class="list-inline mb-0 text-center text-md-end">
              <li class="list-inline-item">
                <router-link class="text-muted" to="/about">About Us</router-link>
              </li>
              <li class="list-inline-item">
                <router-link class="text-muted" to="/privacy">Privacy Policy</router-link>
              </li>
              <li class="list-inline-item">
                <router-link class="text-muted" to="/terms">Terms of Service</router-link>
              </li>
              <li class="list-inline-item">
                <router-link class="text-muted" to="/contact">Support</router-link>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import TheNavbar from '@/components/layout/TheNavbar.vue'
import Toast from '@/components/shared/Toast.vue'

export default defineComponent({
  name: 'BaseLayout',

  components: {
    TheNavbar,
    Toast
  },

  setup() {
    const currentYear = new Date().getFullYear()

    return {
      currentYear
    }
  }
})
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
}

main {
  background-color: #ffffff;
  min-height: calc(100vh - 56px - 80px);
  padding: 2rem 0;
  flex-grow: 1;
}

.footer {
  background-color: #f8f9fa;
  border-top: 1px solid #dee2e6;
}

@media (max-width: 768px) {
  .list-inline-item {
    display: block;
    margin-bottom: 0.5rem;
  }
}
</style>
