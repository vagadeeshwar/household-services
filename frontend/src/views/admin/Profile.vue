<template>
  <div class="container py-5">
    <div class="row justify-content-center g-4">
      <!-- Profile Information -->
      <div class="col-lg-8">
        <ProfileInfo />
      </div>
    </div>
  </div>
</template>

<script>
import ProfileInfo from '@/components/profile/ProfileInfo.vue'

export default {
  name: 'AdminProfile',
  components: {
    ProfileInfo,
  },
}
</script>

<style scoped>
.container {
  max-width: 900px;
}
</style>
